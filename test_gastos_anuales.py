import requests

def test_gastos_anuales():
    url = "http://localhost:9000/api/reportes/gastos-anuales"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ Success!")
            print(response.json())
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_gastos_anuales()
