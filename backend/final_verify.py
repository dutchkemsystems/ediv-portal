import requests
import time

API_KEY = "rnd_1uUl4n2tXxDl3lgVXfRnNNPECJlr"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}
SERVICE_ID = "srv-da6u74gae00c73855d3g"

print("Waiting 3 minutes for build...")
time.sleep(180)

# Check deploy status
resp = requests.get(
    f"https://api.render.com/v1/services/{SERVICE_ID}/deploys",
    headers=HEADERS
)
deploys = resp.json()
latest = deploys[0].get("deploy", deploys[0])
status = latest.get("status", "?")
print(f"Latest deploy: {latest.get('id', '?')} status={status}")

# Try health
print("\nHealth check...")
try:
    h = requests.get("https://ediv-portal.onrender.com/health/", timeout=120)
    print(f"Health: {h.status_code} - {h.text[:200]}")
    
    if h.status_code == 200:
        print("\n=== ALL LOGIN TESTS ===")
        tests = [
            ("admin@ediv.gov.ng", "Admin@12345678", "SYSADMIN"),
            ("tg.ps@ediv.gov.ng", "TutorGen@12345", "TG_PS"),
            ("hr.head@ediv.gov.ng", "HeadOffice@123", "HR"),
            ("finance.head@ediv.gov.ng", "HeadOffice@123", "FIN"),
            ("audit.head@ediv.gov.ng", "HeadOffice@123", "AUDIT"),
            ("emis.head@ediv.gov.ng", "HeadOffice@123", "EMIS"),
            ("qa.head@ediv.gov.ng", "HeadOffice@123", "QA"),
            ("cc.head@ediv.gov.ng", "HeadOffice@123", "CC"),
            ("sa.head@ediv.gov.ng", "HeadOffice@123", "SA"),
            ("registry.head@ediv.gov.ng", "HeadOffice@123", "REG"),
            ("plan.head@ediv.gov.ng", "HeadOffice@123", "PLAN"),
            ("procurement.head@ediv.gov.ng", "HeadOffice@123", "PROC"),
            ("pa.head@ediv.gov.ng", "HeadOffice@123", "PA"),
            ("french.head@ediv.gov.ng", "HeadOffice@123", "FRENCH"),
            ("spd.head@ediv.gov.ng", "HeadOffice@123", "SA_SPD"),
            ("sss.head@ediv.gov.ng", "HeadOffice@123", "QA_SSS"),
            ("principal_apu001@ediv.gov.ng", "SchoolStaff@12345", "PRI"),
            ("principal_mla001@ediv.gov.ng", "SchoolStaff@12345", "PRI"),
            ("vp_apu001@ediv.gov.ng", "SchoolStaff@12345", "VP"),
            ("vp_mla001@ediv.gov.ng", "SchoolStaff@12345", "VP"),
            ("teacher_0001@ediv.gov.ng", "Teacher@12345", "TCH"),
            ("teacher_0100@ediv.gov.ng", "Teacher@12345", "TCH"),
        ]
        
        passed = 0
        failed = 0
        for email, pw, role in tests:
            try:
                r = requests.post(
                    "https://ediv-portal.onrender.com/api/users/auth/",
                    json={"email": email, "password": pw},
                    timeout=30
                )
                if r.status_code == 200 and "access" in r.json():
                    print(f"  PASS  {role:<10} {email}")
                    passed += 1
                else:
                    print(f"  FAIL  {role:<10} {email} - HTTP {r.status_code}")
                    failed += 1
            except Exception as e:
                print(f"  FAIL  {role:<10} {email} - {e}")
                failed += 1
        
        print(f"\n=== RESULTS: {passed} passed, {failed} failed out of {len(tests)} ===")
except Exception as e:
    print(f"Health check: {e}")
