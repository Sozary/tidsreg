import requests

s = requests.Session()
s.post(
    "https://tidsreg.trifork.com/Login?ReturnUrl=/",
    data={"userName": "meay", "password": "bjd5EYH7dzw@bam0etk"}
)
r = s.get("https://tidsreg.trifork.com/Find/SelectProjects?mode=0&customerId=11166")
print(r.status_code, r.text[:500])
