import resources
import json

if __name__ == "__main__":
    datos = resources.obtain_process_data()
    
    for d in datos[:10]:
        json_texto = json.dumps(d, indent=4, ensure_ascii=False)
        print(json_texto)
    
    