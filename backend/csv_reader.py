import csv
import json

def jsonify(data):
    data_dict = {date: value for date, value in data}
    return json.dumps(data_dict)






class CSVReader:
    def preprocess_csv(self, csv_file_path):
        try:
            # Read CSV and replace semicolons with colons
            with open(csv_file_path, 'r', newline='') as csvfile:
                data = csvfile.read()
                data = data.replace(';', ',')
            # Write the modified CSV data back to the file
            with open(csv_file_path, 'w', newline='') as csvfile:
                csvfile.write(data)
                
            print(f"CSV file preprocessed successfully.")
        except FileNotFoundError:
            print(f"Error: File not found - {self.csv_file_path}")
        except Exception as e:
            print(f"An error occurred during CSV preprocessing: {e}")

    def read_csv(self, file_path, member_name):
        try:
            with open(file_path, 'r', newline='') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                extracted_data = []
                for entry in csv_reader:
                    extracted_data.append((entry["date"],entry[member_name]))
                extracted_data.sort()
                return jsonify(extracted_data) if member_name != "" else jsonify(data)
        except FileNotFoundError:
            print(f"Error: File not found - {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

