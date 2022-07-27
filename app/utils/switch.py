from app.googleservice import create_service
import asyncio

zgz_list = ['15HmvU_9ueg_GU_QHlwkjaMg9soZfF_0WwV04xCbwMO0']
mef_list = ['1RND0DAKDWeuyvNYznuIKTqyOq3a-Fdre', '1SNPSEc_JaC_D7XYalI7n_sXCs3SwIAdAkeuql_EzNXw', '1OR8JhDJNUD_uiuMkUGt3RhLHWZ41h7mN', '1TajxSWaJT_bt2Ut4VapoFrhvrR7ZhB9C', '18rxdkbz8Nt6QdTzbRNnu8zIS4G-Ij0nE', '1mxOPo-cGUJM5TavOHJY8mbB3c9X918sjwwCS6Yr__oQ', '1wdBXQk0R9h8dihvcvSofsLiK30sAPdgz', '1s5SjkAMUrvERsT5RoeSf4z23pebyaquU', '1qOIxhFWpZELEbzfm5fk3PNWrX8TKBtBa', '1BeiAlThPRkxgRRJ4TuqDSS6cQmqa69iY', '1wzT5r2k3D8MNo1AiPb8XZdtspx1aML-K', '1K0ioX_7Hf9sf5DyTj5fsx5Uxp-RZpRcG', '1F6U2JTC4ovyB2EqMAczAJXQGD2cvIAPD', '1vw8CC1f7SAaZ2g8UcVJINx9qUyIOja2r', '1ESG3WmU7DAo32KLX5-MFBWv8FBjcn-45']
varam_list =['1rOnUnqOLRYhG3qvk7GnxbqHdmlAryC1A', '1CgEaaTdPuzRA2ZE_5QK1YghGUC3DrJ80', '1Qb7DE7k6ZMtZi2unVIsMBv7R4ezpYgKi', '1WPDfWRw3MLePzBzwOzx5JIbJzYAOMZX2', '1NhG0iw8g4eySX_7sDQMt13DlM0B-W6yY4pMUCvb9VQI', '1xxdTRk2ZAtOqeJQRyPtCsLbWZZm7FMXXydaNCSmhwYY', '1KQRfNOTwnsC-zxOowebPPkftvAgT75MTsdh-BB7O2Mw', '1ZRp3T7hIX7Vb8q-PVwsF7miLXFexRhwg']

service = create_service()

def callback(request_id, response, exception):
    print(response, exception)

zgz_email = "zgz-environment@exemplary-rex-357512.iam.gserviceaccount.com"
mef_email = "mef-environment@exemplary-rex-357512.iam.gserviceaccount.com"
varam_email = "varam-environment@exemplary-rex-357512.iam.gserviceaccount.com"

async def main():
    batch = service.new_batch_http_request(callback=callback)
    for asset_id in varam_list:
        try:
            asset = service.files().get(fileId=asset_id, fields="id").execute()
            batch.add(
                service.permissions().create(
                    fileId=asset["id"],
                    body={
                        'type': 'user',
                        'role': "fileOrganizer",
                        'emailAddress': varam_email
                    },
                    fields='id',
                )
            )
        except Exception as e:
            print(str(e))
    batch.execute()

if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())