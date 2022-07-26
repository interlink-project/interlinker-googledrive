from app.googleservice import create_service
import asyncio

service = create_service()

def callback(request_id, response, exception):
    print(".", end="")

def get_files(service, pageSize=100, pageToken=None):
    results = service.files().list(
            pageSize=pageSize, pageToken=pageToken, fields=f"nextPageToken, files(id)").execute()

    return results.get('nextPageToken', None), results.get('files', [])

async def main():
    cont = True
    token = None
    while cont:
        nextPageToken, assets = get_files(service, pageSize=100, pageToken=token)
        for asset in assets:
            batch = service.new_batch_http_request(callback=callback)
            batch.add(
                service.permissions().create(
                    fileId=asset["id"],
                    sendNotificationEmail=False,
                    body={
                        'type': 'user',
                        'role': "organizer",
                        'emailAddress': "development-environment@exemplary-rex-357512.iam.gserviceaccount.com"
                    },
                    fields='id',
                )
            )
            batch.add(
                service.permissions().create(
                    fileId=asset["id"],
                    sendNotificationEmail=False,
                    body={
                        'type': 'user',
                        'role': "organizer",
                        'emailAddress': "demo-environment@exemplary-rex-357512.iam.gserviceaccount.com"
                    },
                    fields='id',
                )
            )
            batch.add(
                service.permissions().create(
                    fileId=asset["id"],
                    sendNotificationEmail=False,
                    body={
                        'type': 'user',
                        'role': "organizer",
                        'emailAddress': "varam-environment@exemplary-rex-357512.iam.gserviceaccount.com"
                    },
                    fields='id',
                )
            )
            batch.add(
                service.permissions().create(
                    fileId=asset["id"],
                    sendNotificationEmail=False,
                    body={
                        'type': 'user',
                        'role': "organizer",
                        'emailAddress': "mef-environment@exemplary-rex-357512.iam.gserviceaccount.com"
                    },
                    fields='id',
                )
            )
            batch.add(
                service.permissions().create(
                    fileId=asset["id"],
                    sendNotificationEmail=False,
                    body={
                        'type': 'user',
                        'role': "organizer",
                        'emailAddress': "zgz-environment@exemplary-rex-357512.iam.gserviceaccount.com"
                    },
                    fields='id',
                )
            )
            batch.execute()
            
            
        if not nextPageToken:
            cont = False
        else:
            token = nextPageToken


if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())