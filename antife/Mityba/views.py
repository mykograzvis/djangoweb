from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from homepage.models import Product, Receptai, Naudotojai, Valgymai, Valgiarasciai, Recepto_produktai, Naudotojo_receptai, Megstamiausi_receptai, Valgymo_receptas, Valgomas_produktas
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, F, Case, Value, When, Count
from django.contrib.auth import authenticate
from django.contrib import messages
from django.http import JsonResponse
from django import forms
from .forms import ValgymasForm
from decimal import Decimal
from django.core.serializers import serialize
import json
import logging, webbrowser
from django.urls import reverse
from django.db.models import Exists, OuterRef
from django.db import models

logger = logging.getLogger(__name__)

def panaudotireceptai(request):
    # Get the count of each recipe used in Valgymo_receptas
    recipe_counts = Valgymo_receptas.objects.values('fk_Receptasid_Receptas__pavadinimas').annotate(count=Count('fk_Receptasid_Receptas__pavadinimas'))

    # Convert queryset to list of dictionaries
    recipe_counts_list = list(recipe_counts.values('fk_Receptasid_Receptas__pavadinimas', 'count'))

    return render(request, 'PanaudotiReceptai.html', {'recipe_counts': recipe_counts_list})

def valgiarastis(request):
  naudotojas = Naudotojai.objects.get(user=request.user)
  valgiarasciai = Valgiarasciai.objects.filter(fk_Naudotojasid_Naudotojas=naudotojas)
  valgiarasciai_json = serialize('json', valgiarasciai)
  context = {'valgiarasciai_json': valgiarasciai_json}
  return render(request, 'valgiarastis.html', context)

def product(request): 
  query = request.GET.get('query')
  category = request.GET.get('category')

  products = Product.objects.all()
  if query:
    products = products.filter(Q(name__icontains=query))
  if category:
    products = products.filter(category=category)
  return render(request, 'Product.html', {'products': products})

def receptai_list(request):
    # Get all recipes
    all_receptai = Receptai.objects.all()
    
    # Get the current user's favorite recipe IDs
    user_favorite_ids = []
    if request.user.is_authenticated:
        current_user = request.user
        naudotojas = Naudotojai.objects.get(user=current_user)
        user_favorite_ids = Megstamiausi_receptai.objects.filter(fk_Naudotojasid_Naudotojas=naudotojas).values_list('fk_Receptasid_Receptas', flat=True)
    
    # Sort recipes based on whether they are in the user's favorites
    sorted_receptai = sorted(all_receptai, key=lambda r: r.id not in user_favorite_ids)
    
    # Render the template with sorted recipes
    return render(request, 'Receptai.html', {'receptai_list': sorted_receptai, 'user_favorite_ids': user_favorite_ids})
    

@login_required
def manoreceptai_list(request):
    # Get the current user
    current_user = request.user

    try:
        # Get the Naudotojai instance associated with the current user
        naudotojas = Naudotojai.objects.get(user=current_user)
        # Get all recipe IDs associated with the current user from Naudotojo_Receptai table
        user_recipe_ids = Naudotojo_receptai.objects.filter(fk_Naudotojasid_Naudotojas=naudotojas).values_list('fk_Receptasid_Receptas', flat=True)
        # Fetch the recipes from Receptai model using the retrieved recipe IDs
        receptai_list = Receptai.objects.filter(id__in=user_recipe_ids)
    except Naudotojai.DoesNotExist:
        # If the Naudotojai instance for the current user does not exist, return an empty list of recipes
        receptai_list = []

    return render(request, 'ManoReceptai.html', {'manoreceptai_list': receptai_list})


@login_required
def add_to_favorites(request, recipe_id):
    # Get the current user
    current_user = request.user.naudotojai  # Assuming the user profile is accessible via the 'naudotojai' attribute
    
    # Retrieve the recipe
    recipe = get_object_or_404(Receptai, id=recipe_id)
    
    try:
        # Check if the recipe is already in favorites for the current user
        existing_favorite = Megstamiausi_receptai.objects.filter(fk_Receptasid_Receptas=recipe, fk_Naudotojasid_Naudotojas=current_user)
        if existing_favorite.exists():
            # If the recipe is already in favorites, remove it
            existing_favorite.delete()
            return JsonResponse({'status': 'Recipe removed from favorites'})
        else:
            # If the recipe is not in favorites, add it
            Megstamiausi_receptai.objects.create(fk_Receptasid_Receptas=recipe, fk_Naudotojasid_Naudotojas=current_user)
            return JsonResponse({'status': 'Recipe added to favorites'})
    except Exception as e:
        # Handle any exceptions
        return JsonResponse({'error': str(e)}, status=500)

@login_required
#dovydo recepto kurimas
def create_recipe_view(request):
    if request.method == 'POST':
        # Extract form data
        recipe_name = request.POST.get('recipeName')
        recipe_summary = request.POST.get('recipeSummary')
        ingredient_names = request.POST.getlist('ingredient[]')
        ingredient_amounts = request.POST.getlist('amount[]')

        # Check if all required fields are present
        if not (recipe_name and recipe_summary and ingredient_names and ingredient_amounts):
            return JsonResponse({'error': 'Recipe name, summary, ingredients, and amounts are required.'}, status=400)
        
        try:
            # Create Recipe object and save to database
            recipe = Receptai.objects.create(
                pavadinimas=recipe_name,
                aprasas=recipe_summary,
            )
            
            # Check if the recipe was successfully created
            if not recipe:
                return JsonResponse({'error': 'Failed to create recipe.'}, status=500)
            
            # Associate the user's ID with the created recipe
            naudotojas = Naudotojai.objects.get(user=request.user)
            Naudotojo_receptai.objects.create(fk_Naudotojasid_Naudotojas=naudotojas, fk_Receptasid_Receptas=recipe)
            
            total_phe = 0
            total_calories = 0  # Initialize total calories
            total_protein = 0
            
            # Create ingredient objects for the recipe
            for ingredient_name, ingredient_amount in zip(ingredient_names, ingredient_amounts):
                # Get or create the product instance
                product, created = Product.objects.get_or_create(name=ingredient_name)
                
                # Calculate calories and phenylalanine content
                ingredient_amount_decimal = Decimal(ingredient_amount)
                ingredient_calories = ingredient_amount_decimal * (product.calories / Decimal(100))
                total_calories += ingredient_calories
                ingredient_phe = ingredient_amount_decimal * (product.phenylalanine / Decimal(100))
                total_phe += ingredient_phe
                ingredient_protein = ingredient_amount_decimal * (product.protein) / Decimal((100))
                total_protein += ingredient_protein
                
                # Create Recepto_produktai instance
                Recepto_produktai.objects.create(
                    fk_Receptasid_Receptas=recipe,
                    fk_Produktasid_Produktas=product,
                    amount=ingredient_amount_decimal
                )
                
            # Update recipe with total calories and phenylalanine content
            recipe.kalorijos = total_calories
            recipe.fenilalaninas = total_phe
            recipe.baltymai = total_protein
            recipe.save()
            
            # Return success response
            return JsonResponse({'message': 'Recipe created successfully!'})
        
        except Exception as e:
            # Return error response if any exception occurs during creation
            return JsonResponse({'error': str(e)}, status=500)

    # If the request method is not POST, render the template
    products = Product.objects.all()
    product_names = [product.name for product in products]
    return render(request, 'receptukurimas.html', {'products': products, 'product_names': product_names})

def remove_recipe_view(request, recipe_id):
    if request.method == 'POST':
        try:
            # Try to get the recipe object from the database
            recipe = Receptai.objects.get(id=recipe_id)
            # Delete the recipe
            recipe.delete()
            return JsonResponse({'success': True})
        except Receptai.DoesNotExist:
            # If recipe with the provided ID does not exist, return an error
            return JsonResponse({'error': 'Recipe not found.'}, status=404)
        except Exception as e:
            # Return error response if any exception occurs during deletion
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # If the request method is not POST, return a bad request error
        return JsonResponse({'error': 'Bad request.'}, status=400)

def create_valgiarastis(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_date = data.get('date_input')
        naudotojas = Naudotojai.objects.get(user=request.user)

        if selected_date:
            existing_valgiarasciai = Valgiarasciai.objects.filter(data=selected_date, fk_Naudotojasid_Naudotojas=naudotojas)
            
            if existing_valgiarasciai.exists():
                return JsonResponse({'status': 'jau yra'})   
            Valgiarastis = Valgiarasciai.objects.create(
                diena=0,
                bendras_fenilalaninas=0,
                data=selected_date,
                fk_Naudotojasid_Naudotojas=naudotojas
            )
            tipai = ["Pusryčiai", "Pietūs", "Vakarienė", "Papildomi"]
            for tipas in tipai:
                Valgymai.objects.create(
                    tipas=tipas,
                    fk_Valgiarastisid_Valgiarastis=Valgiarastis
                )
            return JsonResponse({'status': 'success'})
    else:
        return render(request, 'valgiarastis.html')
    
def valgymai_open(request):
    selected_date = request.GET.get('selectedDate')
    request.session['selectedDate'] = selected_date
    return valgymai_list(request)

def valgymai_list(request):
    selected_date = request.session.get('selectedDate') 
    naudotojas = Naudotojai.objects.get(user=request.user)

    if selected_date:
        valgiarastis = get_object_or_404(Valgiarasciai, fk_Naudotojasid_Naudotojas=naudotojas, data=selected_date)
        valgymai_list = Valgymai.objects.filter(
            fk_Valgiarastisid_Valgiarastis__data=selected_date,
            fk_Valgiarastisid_Valgiarastis__fk_Naudotojasid_Naudotojas=naudotojas
        ).prefetch_related('valgymo_receptas_set').prefetch_related('valgomas_produktas_set')
    else:
        return render(request, 'valgiarastis.html')
    
    valgymai_list.total_fenilalaninas = 0
    valgymai_list.total_baltymas = 0
    for valgymas in valgymai_list:
        valgymasBalt = 0
        valgymasPhe = 0
        for valgomasreceptas in valgymas.valgymo_receptas_set.all():
            receptas = valgomasreceptas.fk_Receptasid_Receptas
            total_weight = Recepto_produktai.objects.filter(fk_Receptasid_Receptas=receptas).aggregate(total_weight=models.Sum('amount'))['total_weight']
            valgomasreceptas.total_fenilalaninas = round(valgomasreceptas.kiekis /total_weight * Decimal(valgomasreceptas.fk_Receptasid_Receptas.fenilalaninas) , 1)
            valgymasPhe += valgomasreceptas.total_fenilalaninas
            valgymai_list.total_fenilalaninas+=valgomasreceptas.total_fenilalaninas
            valgomasreceptas.total_baltymas = round(valgomasreceptas.kiekis /total_weight * Decimal(valgomasreceptas.fk_Receptasid_Receptas.baltymai) , 1)
            valgymasBalt += valgomasreceptas.total_baltymas
            valgymai_list.total_baltymas+=valgomasreceptas.total_baltymas
        for valgomasproduktas in valgymas.valgomas_produktas_set.all():
            valgomasproduktas.total_fenilalaninas = round(valgomasproduktas.kiekis /100 * Decimal(valgomasproduktas.fk_Produktasid_Produktas.phenylalanine) , 1)
            valgymasPhe += valgomasproduktas.total_fenilalaninas
            valgymai_list.total_fenilalaninas+=valgomasproduktas.total_fenilalaninas
            valgomasproduktas.total_baltymas = round(valgomasproduktas.kiekis /100 * Decimal(valgomasproduktas.fk_Produktasid_Produktas.protein) , 1)
            valgymasBalt += valgomasproduktas.total_baltymas
            valgymai_list.total_baltymas+=valgomasproduktas.total_baltymas
        valgymas.bendras_fenilalaninas = valgymasPhe
        valgymas.bendras_baltymas = valgymasBalt
        valgymas.save()
    valgiarastis.bendras_fenilalaninas = valgymai_list.total_fenilalaninas  
    valgiarastis.bendras_baltymas = valgymai_list.total_baltymas   
    valgiarastis.save()

    specific_naudotojas_receptai = Naudotojo_receptai.objects.filter(fk_Naudotojasid_Naudotojas=naudotojas)
    receptai_ids = specific_naudotojas_receptai.values_list('fk_Receptasid_Receptas', flat=True)

    adminas = Naudotojai.objects.filter(level=2)
    receptai_foradmin = Naudotojo_receptai.objects.filter(fk_Naudotojasid_Naudotojas__in=adminas)
    receptai_ids_level_2 = receptai_foradmin.values_list('fk_Receptasid_Receptas', flat=True)

    all_receptai_ids =  list(receptai_ids_level_2)+ list(receptai_ids)

    context = {
    'valgymai_list': valgymai_list,
    'all_receptai': serialize('json', Receptai.objects.filter(id__in=all_receptai_ids)),
    'all_products': serialize('json', Product.objects.all())
    }
    return render(request, 'valgymas.html', context)

def delete_valgomasReceptas(request, valgymo_receptas_id):
    try:
        valgymo_receptas = Valgymo_receptas.objects.get(id=valgymo_receptas_id)
    except Valgymo_receptas.DoesNotExist:
        return valgymai_list(request)
    if request.method == 'POST':
        valgymo_receptas.delete()
        return valgymai_list(request)
    return valgymai_list(request)
    
def delete_valgomasProduktas(request, valgomas_produktas_id):
    try:
        valgomas_produktas = Valgomas_produktas.objects.get(id=valgomas_produktas_id)
    except Valgomas_produktas.DoesNotExist:
        return valgymai_list(request)
    if request.method == 'POST':
        valgomas_produktas.delete()
        return valgymai_list(request)
    return valgymai_list(request)

def add_new_valgymas(request):
    if request.method == 'GET':
        selected_id = request.GET.get('selectedID')
        selected_name = request.GET.get('selectedName')
        amount = request.GET.get('amount')
        valgymoNr = request.GET.get('buttonIndex')
        selected_date = request.session.get('selectedDate') 
        naudotojas = Naudotojai.objects.get(user=request.user)
        valgiarastis = get_object_or_404(Valgiarasciai, fk_Naudotojasid_Naudotojas=naudotojas, data=selected_date)
        if valgymoNr == '1':
            tipas = "Pusryčiai"
        elif valgymoNr == '2':
            tipas = "Pietūs"
        elif valgymoNr == '3':
            tipas = "Vakarienė"
        else:
            tipas = "Papildomi"
        valgymas = Valgymai.objects.get(fk_Valgiarastisid_Valgiarastis=valgiarastis, tipas=tipas)

        try: # tikrinam ar receptas čia
            receptas = Receptai.objects.get(id=selected_id, pavadinimas=selected_name)
            if not Valgymo_receptas.objects.filter(fk_Receptasid_Receptas=receptas, fk_Valgymasid_Valgymas=valgymas).exists():
                Valgymo_receptas.objects.create(
                    fk_Receptasid_Receptas=receptas,
                    fk_Valgymasid_Valgymas=valgymas,
                    kiekis=amount
                )
        except Receptai.DoesNotExist:
            try:
                produktas = Product.objects.get(id=selected_id, name=selected_name)
                if not Valgomas_produktas.objects.filter(fk_Produktasid_Produktas=produktas, fk_Valgymasid_Valgymas=valgymas).exists():
                    Valgomas_produktas.objects.create(
                        fk_Produktasid_Produktas=produktas,
                        fk_Valgymasid_Valgymas=valgymas,
                        kiekis=amount
                    )
            except Product.DoesNotExist:
                return valgymai_list(request)

    return valgymai_list(request)

def saveCopy(request):
    selected_date = request.session.get('selectedDate')
    print(selected_date)
    request.session['copyDate'] = selected_date
    return valgiarastis(request)

def copyValgiarastis(request):
    naudotojas = Naudotojai.objects.get(user=request.user)
    copyDate = request.session.get('copyDate')
    print(copyDate)
    valgiarastisCopy = get_object_or_404(Valgiarasciai, fk_Naudotojasid_Naudotojas=naudotojas, data=copyDate)
    pasteDate = request.session.get('selectedDate')
    valgiarastisPaste = get_object_or_404(Valgiarasciai, fk_Naudotojasid_Naudotojas=naudotojas, data=pasteDate)
    print(valgiarastisCopy.data)
    print(valgiarastisPaste.data)
    valgiarastisPaste.valgymai_set.all().delete()
    tipai = ["Pusryčiai", "Pietūs", "Vakarienė", "Papildomi"]
    for tipas in tipai:
        valgymas = Valgymai.objects.create(
            tipas=tipas,
            fk_Valgiarastisid_Valgiarastis=valgiarastisPaste
        )
        receptai_to_copy = Valgymo_receptas.objects.filter(fk_Valgymasid_Valgymas__fk_Valgiarastisid_Valgiarastis=valgiarastisCopy, fk_Valgymasid_Valgymas__tipas=tipas)
        for receptas in receptai_to_copy:
            Valgymo_receptas.objects.create(
                fk_Receptasid_Receptas=receptas.fk_Receptasid_Receptas,
                fk_Valgymasid_Valgymas=valgymas,
                kiekis=receptas.kiekis
            )
        produktai_to_copy = Valgomas_produktas.objects.filter(fk_Valgymasid_Valgymas__fk_Valgiarastisid_Valgiarastis=valgiarastisCopy, fk_Valgymasid_Valgymas__tipas=tipas)
        
        for prod in produktai_to_copy:
            Valgomas_produktas.objects.create(
                fk_Produktasid_Produktas=prod.fk_Produktasid_Produktas,
                fk_Valgymasid_Valgymas=valgymas,
                kiekis=prod.kiekis
            )

    return valgymai_list(request)
