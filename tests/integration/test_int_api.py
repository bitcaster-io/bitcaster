#
# import requests
#
#
# def test_run(image, image_name, client):
#     c = client.containers.run(image_name,
#                               ports={8000: 9999},
#                               remove=True,
#                               detach=True)
#     c.stop()
#
#
# def test_client(container):
#     res = requests.get('http://localhost:13141/+api')
#     c = res.json()
#     assert c['result']['login'] == 'http://localhost:13141/+login'
