from flask import Flask, render_template, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

plt.switch_backend('Agg')

app = Flask(__name__)
data = pd.read_excel('Data_Timbulan_Sampah_SIPSN_KLHK.xlsx')
data.columns = ['Tahun', 'Provinsi', 'Kabupaten/Kota', 'Timbulan Sampah Harian (ton)', 'Timbulan Sampah Tahunan (ton)']
data = data.drop(0)
data['Tahun'] = data['Tahun'].astype(int)
data['Timbulan Sampah Tahunan (ton)'] = data['Timbulan Sampah Tahunan (ton)'].astype(float)

data = data[data['Tahun'] != 2018]

total_annual_waste = data.groupby(['Tahun', 'Provinsi'])['Timbulan Sampah Tahunan (ton)'].sum().reset_index()

average_annual_waste = total_annual_waste.groupby('Provinsi')['Timbulan Sampah Tahunan (ton)'].mean().reset_index()
average_annual_waste.columns = ['Provinsi', 'Average Annual Waste (ton)']

def categorize_province(waste):
    if waste <= 100000:
        return 'GREEN'
    elif waste <= 700000:
        return 'ORANGE'
    else:
        return 'RED'

average_annual_waste['Category'] = average_annual_waste['Average Annual Waste (ton)'].apply(categorize_province)

category_counts = average_annual_waste['Category'].value_counts().reindex(['GREEN', 'ORANGE', 'RED'], fill_value=0)

@app.route('/total_annual_waste')
def total_annual_waste_graph():
    plt.figure(figsize=(12, 8))
    for province in total_annual_waste['Provinsi'].unique():
        province_data = total_annual_waste[total_annual_waste['Provinsi'] == province]
        plt.plot(province_data['Tahun'], province_data['Timbulan Sampah Tahunan (ton)'], label=province)
    plt.title('Total Annual Waste Generation in Each Province Over the Years')
    plt.xlabel('Year')
    plt.ylabel('Total Annual Waste (tons)')
    plt.legend()
    plt.grid(True)
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return f'<img src="data:image/png;base64,{img_base64}"/>'

@app.route('/total_annual_waste_specific')
def total_annual_waste_specific_graph():
    provinces_of_interest = ['Jawa Barat', 'Jawa Tengah', 'Jawa Timur']
    filtered_data = total_annual_waste[total_annual_waste['Provinsi'].isin(provinces_of_interest)]
    
    plt.figure(figsize=(12, 8))
    for province in filtered_data['Provinsi'].unique():
        province_data = filtered_data[filtered_data['Provinsi'] == province]
        plt.plot(province_data['Tahun'], province_data['Timbulan Sampah Tahunan (ton)'], label=province)
    plt.title('Total Annual Waste Generation in Jawa Barat, Jawa Tengah, and Jawa Timur Over the Years')
    plt.xlabel('Year')
    plt.ylabel('Total Annual Waste (tons)')
    plt.legend()
    plt.grid(True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return f'<img src="data:image/png;base64,{img_base64}"/>'

@app.route('/average_annual_waste')
def average_annual_waste_categorization():
    plt.figure(figsize=(10, 6))
    plt.barh(average_annual_waste['Provinsi'], average_annual_waste['Average Annual Waste (ton)'], color=average_annual_waste['Category'].map({'GREEN': 'green', 'ORANGE': 'orange', 'RED': 'red'}))
    plt.title('Average Annual Waste Generation by Province')
    plt.ylabel('Province')
    plt.xlabel('Average Annual Waste (tons)')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return f'<img src="data:image/png;base64,{img_base64}"/>'

@app.route('/average_annual_waste_category_count')
def average_annual_waste_category_count():
    plt.figure(figsize=(10, 6))
    plt.bar(category_counts.index, category_counts.values, color=['green', 'orange', 'red'])
    plt.title('Categorization of Average Annual Waste Generation in Each Province')
    plt.xlabel('Category')
    plt.ylabel('Number of Provinces')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return f'<img src="data:image/png;base64,{img_base64}"/>'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
