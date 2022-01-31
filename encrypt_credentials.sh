gpg --symmetric --cipher-algo AES256 credentials.json 
echo "REMEMBER TO SET THIS PASSWORD ON GITHUB ENV VARIABLES"

# decrypt
# gpg --quiet --batch --yes --decrypt --passphrase="${{ secrets.GOOGLE_API_PW }}" --output credentials.json credentials.json.gpg