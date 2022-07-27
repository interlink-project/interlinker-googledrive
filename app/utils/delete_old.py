# script for deleting 1000 old resources

from app.googleservice import create_service

raise Exception("Remove this line to execute it")
def get_files(service, pageSize=1000, pageToken=None):
    results = service.files().list(
            pageSize=pageSize, pageToken=pageToken, orderBy="createdTime asc", fields=f"nextPageToken, files(id, createdTime)").execute()

    return results.get('nextPageToken', None), results.get('files', [])

service = create_service()
print("starting")
nextPageToken, files = get_files(service)
batch = service.new_batch_http_request()

for file in files:
    print(file.get("id"))
    batch.add(service.files().delete(fileId=file.get("id")))

batch.execute()