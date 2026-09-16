import urllib.request
import urllib.error
import json
import time

def run_tests():
    print("=== Running Live Vynk Full-Stack Verification ===")
    ts_suffix = int(time.time())

    # 1. Test Landing Page on Frontend server
    with urllib.request.urlopen('http://127.0.0.1:5173/') as res:
        frontend_html = res.read().decode('utf-8')
        assert 'Vynk' in frontend_html, 'Vynk not found in frontend HTML'
        print("[PASS] 1. Frontend dev server is serving Vynk application (200 OK)")

    # 2. Test Backend Health on Backend server
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/health')
    with urllib.request.urlopen(req) as res:
        health = json.loads(res.read().decode('utf-8'))
        assert health['status'] == 'healthy', 'Health check failed'
        print(f"[PASS] 2. Backend health check passed: {health['status']} (DB latency: {health['database']['latency_ms']}ms)")

    # 3. Test Registration via Backend (Entrepreneur)
    founder_email = f'live.founder.{ts_suffix}@vynk.io'
    reg_data = json.dumps({
        'email': founder_email,
        'password': 'LivePassword123!',
        'full_name': 'Live Test Founder',
        'role': 'entrepreneur',
        'stage': 'mvp',
        'industry': 'CleanTech'
    }).encode('utf-8')
    reg_req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/auth/register',
        data=reg_data,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(reg_req) as res:
        token_data = json.loads(res.read().decode('utf-8'))
        assert 'access_token' in token_data, 'No access token'
        token = token_data['access_token']
        print(f"[PASS] 3. Live registration succeeded for Entrepreneur: {token_data['email']}")

    # 4. Test Protected Route with JWT
    me_req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/auth/me',
        headers={'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(me_req) as res:
        me_data = json.loads(res.read().decode('utf-8'))
        assert me_data['role'] == 'entrepreneur', 'Role mismatch'
        assert me_data['trust_score']['score'] == 50, 'Trust score mismatch'
        print(f"[PASS] 4. Protected /auth/me succeeded: user={me_data['full_name']}, trust={me_data['trust_score']['score']}/100")

    # 5. Test Login with valid credentials
    login_data = json.dumps({
        'email': founder_email,
        'password': 'LivePassword123!'
    }).encode('utf-8')
    login_req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/auth/login',
        data=login_data,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(login_req) as res:
        login_res = json.loads(res.read().decode('utf-8'))
        assert 'access_token' in login_res
        print("[PASS] 5. Live login succeeded with JWT verification")

    # 6. Test Invalid Login rejection
    bad_data = json.dumps({
        'email': founder_email,
        'password': 'WrongPassword999!'
    }).encode('utf-8')
    bad_req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/auth/login',
        data=bad_data,
        headers={'Content-Type': 'application/json'}
    )
    try:
        urllib.request.urlopen(bad_req)
        assert False, 'Expected 401 Unauthorized'
    except urllib.error.HTTPError as e:
        assert e.code == 401
        print("[PASS] 6. Invalid password correctly rejected with 401 Unauthorized")

    # 7. Test Sponsor Registration & Role separation
    spon_email = f'live.sponsor.{ts_suffix}@vynk.io'
    spon_data = json.dumps({
        'email': spon_email,
        'password': 'LivePassword123!',
        'full_name': 'Live Test Sponsor',
        'role': 'sponsor',
        'organization_name': 'Horizon Impact Partners',
        'sponsor_type': 'venture_fund',
        'min_budget': 10000,
        'max_budget': 200000
    }).encode('utf-8')
    spon_req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/auth/register',
        data=spon_data,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(spon_req) as res:
        spon_res = json.loads(res.read().decode('utf-8'))
        spon_token = spon_res['access_token']
        print(f"[PASS] 7. Live sponsor registration succeeded: {spon_res['role']}")

    # 8. Test Project Creation by Entrepreneur
    proj_data = json.dumps({
        'title': 'SolarClean Bioreactor Live',
        'tagline': 'Scalable outdoor photobioreactor for CO2 capture',
        'description': 'Modular biological carbon capture units',
        'category': 'CleanTech',
        'stage': 'mvp',
        'funding_goal': 50000.0,
        'requirements': [{'requirement_type': 'capital', 'title': 'Pilot units', 'amount': 50000.0}]
    }).encode('utf-8')
    proj_req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/projects/',
        data=proj_data,
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(proj_req) as res:
        proj = json.loads(res.read().decode('utf-8'))
        proj_id = proj['id']
        print(f"[PASS] 8. Live project created: '{proj['title']}' (id={proj_id})")

    # 9. Test Sponsor Creating Commitment on Project
    comm_data = json.dumps({
        'project_id': proj_id,
        'amount': 35000.0,
        'sponsorship_type': 'grant',
        'status': 'interested',
        'notes': 'Initial grant tranche'
    }).encode('utf-8')
    comm_req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/commitments/',
        data=comm_data,
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {spon_token}'}
    )
    with urllib.request.urlopen(comm_req) as res:
        comm = json.loads(res.read().decode('utf-8'))
        comm_id = comm['id']
        print(f"[PASS] 9. Live sponsorship commitment created: id={comm_id}, amount=${comm['amount']:,.2f}, status={comm['status']}")

    # 10. Test Progression: Interested -> Discussion -> Promised -> Confirmed -> Completed
    for next_st, note in [
        ('discussion', 'Technical review call complete'),
        ('promised', 'Term sheet delivered'),
        ('confirmed', 'Agreement executed'),
        ('completed', 'Tranche disbursed')
    ]:
        patch_data = json.dumps({'new_status': next_st, 'note': note}).encode('utf-8')
        patch_req = urllib.request.Request(
            f'http://127.0.0.1:8000/api/v1/commitments/{comm_id}/status',
            data=patch_data,
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {spon_token}'},
            method='PATCH'
        )
        with urllib.request.urlopen(patch_req) as res:
            p_json = json.loads(res.read().decode('utf-8'))
            assert p_json['status'] == next_st
            print(f"   -> Progressed commitment to '{next_st}'")

    # 11. Test Trust Score Reward verification
    trust_req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/trust/me',
        headers={'Authorization': f'Bearer {spon_token}'}
    )
    with urllib.request.urlopen(trust_req) as res:
        t_data = json.loads(res.read().decode('utf-8'))
        assert t_data['completed_commitments_count'] >= 1
        assert t_data['score'] >= 55
        print(f"[PASS] 10. Verifiable Trust Score updated: {t_data['score']}/100 (Fulfilled commitments: {t_data['completed_commitments_count']})")

    # 12. Test AI Service layer endpoint (readiness verification)
    ai_req = urllib.request.Request('http://127.0.0.1:8000/api/v1/ai/status')
    with urllib.request.urlopen(ai_req) as res:
        ai_stat = json.loads(res.read().decode('utf-8'))
        assert ai_stat['provider'] == 'gemini'
        print(f"[PASS] 11. AI Service layer verified: provider={ai_stat['provider']}, mode={ai_stat['mode']}")

    print("\nSUCCESS: ALL 11 LIVE ARCHITECTURE & FUNCTIONALITY CHECKS PASSED!")

if __name__ == '__main__':
    run_tests()
