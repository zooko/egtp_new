#include "integer.h"
#include "wrappedrsa.h"
#include "stdio.h"
#include "randsource_methods.h"
#include "cryptlib.h"
#include <iostream>

USING_NAMESPACE(CryptoPP)

void spew(char* vname,Integer val)
{
	byte *garbage = new byte[25];
	int garlen = 0;
	int x;
	garlen = val.Encode(garbage,25);
	printf("%s = ",vname);
	for(x = 0;x < garlen;x++)
	{
		printf("%02x",garbage[x]);
	}
	printf("\n");
}

int encode_and_decode()
{
	printf("encode_and_decode() 0\n");
	byte buf[20] = { 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X' };
	randsource_add(buf, 20, 160);
	Integer e(3);
	WrappedRSAFunction func(88,e);
	std::string s = func.PrivateKeyEncoding();
	printf("encode_and_decode() 1\n");
	StringStore bt(s);
	printf("encode_and_decode() 2\n");
	WrappedRSAFunction* f2 = new WrappedRSAFunction(bt);
	printf("(func.GetModulus() == f2->GetModulus()); ");
	printf("%d\n", (func.GetModulus() == f2->GetModulus()));
	assert (func.GetModulus() == f2->GetModulus());
	printf("(func.GetExponent() == f2->GetExponent()); ");
	printf("%d\n", (func.GetExponent() == f2->GetExponent()));
	assert (func.GetExponent() == f2->GetExponent());
	std::string s2 = f2->PrivateKeyEncoding();
	printf("(s == s2);");
	printf("%d\n", (s == s2));
	assert (s == s2);
	printf("encode_and_decode() finished\n");
}

int main(int argc,char *argv[])
{
	encode_and_decode();
	byte buf[20] = { 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X' };
	randsource_add(buf, 20, 160);

	Integer e(3);
	printf("start HELLO\n");
	WrappedRSAFunction func(88,e);
	Integer n = func.GetModulus();
	spew("e",func.GetExponent());
	spew("n",n);
	Integer plaintext(50034097);
	spew("plaintext",plaintext);
	Integer ciphertext(func.ApplyFunction(plaintext));
	spew("ciphertext",ciphertext);
	Integer replaintext(func.CalculateInverse(ciphertext));
	spew("recalculated plaintext",replaintext);
	
	printf("\n");
	WrappedRSAFunction clientfunc(n,e);
	spew("client's n",clientfunc.GetModulus());
	spew("client's e",clientfunc.GetExponent());
	// c
	Integer coin(3254098);
	spew("coin",coin);
	// b
	Integer blind(235234);
	spew("blinding factor",blind);
	// b ** e
	Integer encryptedBlind = clientfunc.ApplyFunction(blind);
	spew("encrypted blinding factor",encryptedBlind);
	// c * (b ** e)
	Integer forServer = clientfunc.Multiply(coin,encryptedBlind);
	spew("blinded value sent to server",forServer);

	// (c ** d) * b
	Integer signedval = func.CalculateInverse(forServer);
	spew("value returned by server",signedval);
	
	Integer referenceSignedCoin = func.CalculateInverse(coin);
	spew("directly calculated signed coin",referenceSignedCoin);
	
	Integer verifySignedCoin = func.ApplyFunction(referenceSignedCoin);
	spew("verification of signed coin (should be equal to coin)",verifySignedCoin);
	
	Integer signedCoin = clientfunc.Divide(signedval,blind);
	spew("signed coin",signedCoin);
	
	Integer unsignedCoin = clientfunc.ApplyFunction(signedCoin);
	spew("signed value (hopefully the same as coin)",unsignedCoin);
}
