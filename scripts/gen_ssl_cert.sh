#!/bin/sh

PRIVATE_KEY_NAME="private.key"
CSR_NAME="certificate.csr"
CERT_NAME="certificate.crt"
RSA_KEY_SIZE=2048

# generate an RSA SSL cert
openssl genrsa -out $PRIVATE_KEY_NAME $RSA_KEY_SIZE
openssl rsa -in $PRIVATE_KEY_NAME -out $PRIVATE_KEY_NAME
openssl req -sha256 -new -key $PRIVATE_KEY_NAME -out $CSR_NAME -subj '/CN=localhost'
openssl x509 -req -sha256 -days 365 -in $CSR_NAME -signkey $PRIVATE_KEY_NAME -out $CERT_NAME


# use RSA crypto
#openssl genrsa -out $PRIVATE_KEY_NAME $RSA_KEY_SIZE
#openssl rsa -in $PRIVATE_KEY_NAME -outform PEM -pubout -out public.pem
# use eliptic curve crypto
#openssl ecparam -name prime256v1 -genkey -noout -out $PRIVATE_KEY_NAME
#openssl ec -in $PRIVATE_KEY_NAME -pubout -out public.pem
