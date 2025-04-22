def test_registration(client):
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data


def test_login(client):
    # First register a user
    client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass'
    })

    # Then test login
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Profile' in response.data