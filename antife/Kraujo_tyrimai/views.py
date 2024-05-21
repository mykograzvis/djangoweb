from django.shortcuts import render, redirect
from homepage.models import Kraujo_tyrimai, Naudotojai
from django.contrib.auth.decorators import login_required
from .utils import get_plot
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
import datetime
from datetime import datetime
import plotly.express as px

@login_required
def create_kraujo_tyrimas(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        fenilalaninas = request.POST.get('fenilalaninas')
        selected_year = int(request.POST.get('selected_year'))  # Retrieve selected year
        
        # Check if both data and fenilalaninas are empty
        if not data or not fenilalaninas:
            messages.error(request, 'Užpildykite formą')
            return redirect('kraujo_tyrimai:kraujotyrview', selected_year=selected_year)  # Pass selected year
        
        # Fetch the corresponding Naudotojai instance
        naudotojai_instance = Naudotojai.objects.get(user=request.user)
        
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        today = datetime.now().date()
        
        if data_obj > today:
            # If the selected date is greater than today's date, display an error message
            messages.error(request, 'Pasirinkta negalima data.')
            return redirect('kraujo_tyrimai:kraujotyrview', selected_year=selected_year)  # Pass selected year
        
        # Check if a Kraujotyr already exists for the given date and user
        existing_kraujotyr = Kraujo_tyrimai.objects.filter(Q(data=data) & Q(fk_Naudotojasid_Naudotojas=naudotojai_instance)).exists()
        if existing_kraujotyr:
            # If a Kraujotyr already exists for the given date and user, show an error message
            messages.error(request, 'Kraujo tyrimas su šia data jau egzistuoja.')
        else:
            # If a Kraujotyr for the given date and user doesn't exist, create a new one
            Kraujo_tyrimai.objects.create(data=data, fenilalaninas=fenilalaninas, fk_Naudotojasid_Naudotojas=naudotojai_instance)
            # Add success message
            messages.success(request, 'Kraujo tyrimas sėkmingai pridėtas.')
        
        # Redirect to the 'kraujotyrview' view with the selected year
        return redirect('kraujo_tyrimai:kraujotyrview', selected_year=selected_year)

    # If the request method is not POST, render the 'kraujotyrview' template
    return redirect('kraujo_tyrimai:kraujotyrview')


@login_required
def kraujotyrview(request, selected_year=None):  # Add selected_year as a parameter with a default value of None
    # Filter Kraujo_tyrimai instances by the current authenticated user
    kraujo_tyrimai_qs = Kraujo_tyrimai.objects.filter(fk_Naudotojasid_Naudotojas__user=request.user)
    
    if not kraujo_tyrimai_qs:
        # If there are no kraujo tyrimai, render the template without the chart
        return render(request, 'Kraujotyr.html')

    # Extract x (dates) and y (fenilalaninas) data
    x = [kraujo_tyrimas.data for kraujo_tyrimas in kraujo_tyrimai_qs]
    y = [kraujo_tyrimas.fenilalaninas for kraujo_tyrimas in kraujo_tyrimai_qs]
    
    # Combine dates and phenylalanine values into tuples
    data_points = list(zip(x, y))
    
    # Sort the data points based on dates
    sorted_data_points = sorted(data_points, key=lambda tup: tup[0])
    
    if not sorted_data_points:
        # If there are no data points, render the template without the chart
        return render(request, 'Kraujotyr.html')

    # Extract sorted dates and phenylalanine
    sorted_dates, sorted_phenylalanine = zip(*sorted_data_points)
    
    # Get unique years
    years = sorted(set(date.year for date in sorted_dates))
    
    # Initialize selected_year outside the conditional block
    if selected_year is None:
        selected_year = years[-1]  # By default, show data points for the most recent year
    
    # Handle form submission
    if request.method == 'POST':
        selected_year = int(request.POST.get('year'))
    
    # Filter data points for the selected year
    filtered_data_points = [(date, phenylalanine) for date, phenylalanine in sorted_data_points if date.year == selected_year]
    # Unzip filtered data points into separate lists
    sorted_dates, sorted_phenylalanine = zip(*filtered_data_points)
    
    # Define color thresholds
    green_zone = (120, 600)
    orange_threshold = 800  # Adjust as needed
    
    # Assign colors to data points based on proximity to thresholds
    colors = []
    for phenylalanine in sorted_phenylalanine:
        if phenylalanine >= green_zone[0] and phenylalanine <= green_zone[1]:
            colors.append('green')  # Green zone
        elif phenylalanine > orange_threshold:
            colors.append('red')  # Far from good zone
        else:
            colors.append('orange')  # Close to good zone
    
    # Convert sorted dates to formatted Lithuanian month names
    lithuanian_month_names = {
        1: 'Sausio',
        2: 'Vasario',
        3: 'Kovo',
        4: 'Balandžio',
        5: 'Gegužės',
        6: 'Birželio',
        7: 'Liepos',
        8: 'Rugpjūčio',
        9: 'Rugsėjo',
        10: 'Spalio',
        11: 'Lapkričio',
        12: 'Gruodžio'
    }
    formatted_dates = [f"{date.strftime('%Y')} - {lithuanian_month_names[date.month]} {date.day}" for date in sorted_dates]
    
    # Create the plot
    fig = px.line(y=sorted_phenylalanine, x=formatted_dates, labels={'x': 'Data', 'y': 'Fenilalaninas µmol/l'},
                  hover_name=[date.strftime('%Y %B %d') for date in sorted_dates])  # Set hover_name to formatted dates
    
    # Add scatter markers with colored points and disable legend
    fig.add_scatter(x=formatted_dates, y=sorted_phenylalanine, mode='markers', marker=dict(size=10, color=colors), showlegend=False, hoverinfo='text')

    # Customize hover text
    hover_text = 'Fenilalaninas: %{y}<br>Data: %{x}'
    fig.update_traces(hovertemplate=hover_text)

    # Determine the maximum value of Fenilalaninas
    max_fenilalaninas = max(sorted_phenylalanine)
    
    # Set the default range for the y-axis
    y_axis_upper_limit = max_fenilalaninas * 1.1  # Increase by 10% for padding
    fig.update_layout(yaxis=dict(range=[0, y_axis_upper_limit]))
    
    # Define the green background zone
    fig.update_layout(
        shapes=[
            # Green rectangle for the background
            {
                'type': 'rect',
                'x0': formatted_dates[0],  # Start date of the green zone
                'x1': formatted_dates[-1],  # End date of the green zone
                'y0': green_zone[0],  # Lower limit of the y-axis
                'y1': green_zone[1],  # Upper limit of the y-axis
                'fillcolor': 'rgba(173, 255, 47, 0.2)',  # Green color with opacity
                'line': {'width': 0},  # No border line
                'layer': 'below',  # Ensure the green zone is below the main plot
            },
        ]
    )
    
    # Convert plot to HTML
    chart = fig.to_html()
    
    context = {'chart': chart, 'years': years, 'selected_year': selected_year}
    
    return render(request, 'kraujotyr.html', context)