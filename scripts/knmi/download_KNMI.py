from datetime import datetime, timedelta
import requests

api_url = "https://api.dataplatform.knmi.nl/open-data"


def main():
    # Parameters
    api_key = ""
    dataset_name = "rad_nl25_rac_mfbs_5min"
    dataset_version = "2"
    max_keys = "10"

    timestamp_now = datetime.utcnow()
    timestamp_one_hour_ago = timestamp_now - timedelta(hours=1) - timedelta(minutes=timestamp_now.minute % 10)
    filename = f"RADNL_CLIM____MFBSNL25_05m_220171231T235500_20181231T235500_0002.zip"
    endpoint = f"{api_url}/datasets/{dataset_name}/versions/{dataset_version}/files/{filename}/url"
    get_file_response = requests.get(endpoint, headers={"Authorization": api_key})
    download_url = get_file_response.json().get("temporaryDownloadUrl")
    dataset_file = requests.get(download_url)

if  __name__ == "__main__":
    main()
    
    
    
