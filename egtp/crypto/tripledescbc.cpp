// This is actually a C++ file - it's got a .c extension to make make happy

// This is actually DES-X, not triple DES.

#include <iostream> // for couts for debugging

#include "modes.h"
#include "des.h"
#include "filters.h"

//extern "C"
//{
#include "Python.h"
//}

USING_NAMESPACE(CryptoPP)

PyObject *TripleDESCBCError;

class MemoryException : public std::exception
{
public:
	explicit MemoryException() {}
	virtual ~MemoryException() throw() {}
};

#define xdelete(p) delete (p); p = NULL
#define xdeletear(p) delete[] (p); p = NULL

typedef struct
{
	PyObject_HEAD
	byte *key;
} tripledescbc;

static PyObject *tripledescbc_new(tripledescbc *self, PyObject *args);

static void tripledescbc_delete(tripledescbc *self);

static PyObject *tripledescbc_encrypt(tripledescbc *self, PyObject *args);

static PyObject *tripledescbc_decrypt(tripledescbc *self, PyObject *args);

static PyObject *tripledescbc_getattr(tripledescbc *self, char* name);

statichere PyTypeObject tripledescbc_type = {
        PyObject_HEAD_INIT(&PyType_Type)
        0,                        /*ob_size*/
        "DES-XEX3CBC",                  /*tp_name*/
        sizeof(tripledescbc),        /*tp_size*/
        0,                        /*tp_itemsize*/
        /* methods */
        (destructor)tripledescbc_delete,  /*tp_dealloc*/
        0,                        /*tp_print*/
        (getattrfunc)tripledescbc_getattr, /*tp_getattr*/
        0,                        /*tp_setattr*/
        0,                        /*tp_compare*/
        0,                        /*tp_repr*/
        0,                        /*tp_as_number*/
        0,                        /*tp_as_sequence*/
        0,                        /*tp_as_mapping*/
        0,                        /*tp_hash*/
        0,                        /*tp_call*/
        0,                        /*tp_str*/
        0,                        /*tp_getattro*/
        0,                        /*tp_setattro*/
        0,                        /*tp_as_buffer*/
        0,                        /*tp_xxx4*/
        0,                        /*tp_doc*/
};

static PyMethodDef tripledescbc_methods[] = {
  {"encrypt", (PyCFunction)tripledescbc_encrypt, METH_VARARGS, 
   "Returns an encrypted string.\n"
   "Accepts an IV string of length 8 and a plaintext string.\n"
   "Encrypts in CBC mode with ciphertext stealing.\n"
   "Always returns a ciphertext of the exact same length as the plaintext."
  }, 
  {"decrypt", (PyCFunction)tripledescbc_decrypt, METH_VARARGS, 
   "Returns a decrypted string.\n"
   "Accepts an IV string of length 8 and a ciphertext string.\n"
   "Decrypts in CBC mode with ciphertext stealing.\n"
   "Always returns a plaintext of the exact same length as the ciphertext."
  }, 
  {NULL, NULL}	/* sentinel */
};

static PyObject *tripledescbc_getattr(tripledescbc *self, char* name)
{
	return Py_FindMethod(tripledescbc_methods, (PyObject *)self, name);
}

static void tripledescbc_delete(tripledescbc *self) {
	if(self != NULL) {
		xdeletear(self->key);
		PyMem_DEL(self);
	}
}

static PyObject *tripledescbc_new(tripledescbc *self, PyObject *args) {
	tripledescbc *newself = NULL;
	try {
		byte *key;
		int keylength;
		if(!PyArg_ParseTuple(args, "s#", &key, &keylength)) {
			throw Exception(Exception::INVALID_ARGUMENT, "wrong type of parameters passed in from Python");
		}
		if(keylength != 24) {
			throw Exception(Exception::INVALID_ARGUMENT, "triple DES key length must be 24");
		}
		if(!(newself = PyObject_New(tripledescbc, &tripledescbc_type))) {
		  throw MemoryException();
		}
		byte *keycopy = new byte[24];
		memcpy(keycopy, key, 24);
		//		printf("in tripledescbc_new(); keycopy: %p, key: %p\n", keycopy, key);
		newself->key = keycopy;
		return (PyObject *)newself;
	}
	catch(CryptoPP::Exception &e) {
		tripledescbc_delete(newself);
		PyErr_SetString(TripleDESCBCError, e.what());
		return NULL;
	}
	catch(MemoryException &e)
	{
		tripledescbc_delete(newself);
		PyErr_SetString(PyExc_MemoryError, "Can't allocate memory to do set up keys for en/decryption");
		return NULL;
	}
}

#define _MIN_UNSAFE(x, y) ((x)<(y)?(x):(y))
static PyObject *tripledescbc_encrypt(tripledescbc *self, PyObject *args) {
	//	std::cout << "hello enc 0" << std::endl; std::cout.flush();
	PyObject *result = NULL;
	byte *ciphertext = NULL;
	try {
		byte *iv;
		unsigned int ivlength;
		byte *text;
		unsigned int textlength;
		if(!PyArg_ParseTuple(args, "s#s#", &iv, &ivlength, &text, &textlength)) {
			throw Exception(Exception::INVALID_ARGUMENT, "wrong type of parameters passed in from Python");
		}
		if(ivlength != 8) {
			throw Exception(Exception::INVALID_ARGUMENT, "IV length must be 8");
		}
		//		std::cout << "hello enc 0.7" << std::endl; std::cout.flush();
		//		std::cout << "hello enc 0.7.1, self: " << self << std::endl; std::cout.flush();
		//		std::cout << "hello enc 0.7.2, self->key: ";
		//		std::cout << self->key;
		//		std::cout << std::endl;
		//		std::cout.flush();
		//	std::cout << "hello enc 0.7.3, iv: " << iv << std::endl; std::cout.flush();
		CBC_CTS_Mode<DES_XEX3>::Encryption encryption(self->key, 24, iv);
		//		std::cout << "hello enc 0.8" << std::endl; std::cout.flush();
		ciphertext = new byte[textlength];
		//		std::cout << "hello enc 0.9" << std::endl; std::cout.flush();
		if (ciphertext == NULL) {
			throw MemoryException();
		}
		//		std::cout << "hello enc 1" << std::endl; std::cout.flush();
		StreamTransformationFilter encryptor(encryption, new ArraySink(ciphertext, textlength));
		//		std::cout << "hello enc 2" << std::endl; std::cout.flush();
		encryptor.PutMessageEnd(text, textlength);
		//		std::cout << "hello enc 3" << std::endl; std::cout.flush();
		result = Py_BuildValue("s#", ciphertext, textlength);
		//		std::cout << "hello enc 4" << std::endl; std::cout.flush();
		if(result == NULL) {
			throw MemoryException();
		}
		//		std::cout << "hello enc 5" << std::endl; std::cout.flush();
		xdeletear(ciphertext);
		//		std::cout << "hello enc 6" << std::endl; std::cout.flush();
		return result;
	}
	catch(CryptoPP::Exception &e) {
		if(result != NULL) {
			PyMem_DEL(result);
		}
		xdeletear(ciphertext);
		PyErr_SetString(TripleDESCBCError, e.what());
		return NULL;
	}
	catch(MemoryException &e) {
		if(result != NULL) {
			PyMem_DEL(result);
		}
		xdeletear(ciphertext);
		PyErr_SetString(PyExc_MemoryError, "Can't allocate memory to do encryption");
		return NULL;
	}
	//	std::cout << "goodbye enc" << std::endl; std::cout.flush();
}

static PyObject *tripledescbc_decrypt(tripledescbc *self, PyObject *args) {
	//	std::cout << "hello dec 0" << std::endl; std::cout.flush();
	PyObject *result = NULL;
	byte *plaintext = NULL;
	try {
		byte *iv;
		unsigned int ivlength;
		byte *text;
		unsigned int textlength;
		if(!PyArg_ParseTuple(args, "s#s#", &iv, &ivlength, &text, &textlength)) {
			throw Exception(Exception::INVALID_ARGUMENT, "wrong type of parameters passed in from Python");
		}
		if(ivlength != 8) {
			throw Exception(Exception::INVALID_ARGUMENT, "IV length must be 8");
		}
		CBC_CTS_Mode<DES_XEX3>::Decryption decryption(self->key, 24, iv);
		plaintext = new byte[textlength];
		if (plaintext == NULL) {
			throw MemoryException();
		}
		StreamTransformationFilter decryptor(decryption, new ArraySink(plaintext, textlength));
		decryptor.PutMessageEnd(text, textlength);
		result = Py_BuildValue("s#", plaintext, textlength);
		if(result == NULL) {
			throw MemoryException();
		}
		xdeletear(plaintext);
		return result;
	}
	catch(CryptoPP::Exception &e) {
		if(result != NULL) {
			PyMem_DEL(result);
		}
		xdeletear(plaintext);
		PyErr_SetString(TripleDESCBCError, e.what());
		return NULL;
	}
	catch(MemoryException &e) {
		if(result != NULL) {
			PyMem_DEL(result);
		}
		xdeletear(plaintext);
		PyErr_SetString(PyExc_MemoryError, "Can't allocate memory to do decryption");
		return NULL;
	}
}

PyMethodDef tripledescbc_functions[] = {
  {"new", (PyCFunction)tripledescbc_new, METH_VARARGS, 
   "Constructs a new tripledescbc.\n"
   "Accepts a key of length 24."
  }, 
  {NULL, NULL}	/* Sentinel */
};

char* tripledescbc_doc =
"Does 3DES encryption and decyption in CBC mode with ciphertext stealing.\n"
"Always uses a key of length 24 and initialization vectors of length 8.\n"
"\n"
"Class methods are - \n"
"new(key) - constructor\n"
"\n"
"Instance methods are - \n"
"encrypt(iv, plaintext) - encrypt a string\n"
"decrypt(iv, ciphertext) - decrypt a string";

/* Initialize this module. */

extern "C"
{
DL_EXPORT(void)
inittripledescbc()
{
        PyObject *m, *d;
	m = Py_InitModule3("tripledescbc", tripledescbc_functions, tripledescbc_doc);
        d = PyModule_GetDict(m);
        TripleDESCBCError = PyErr_NewException("tripledescbc.Error", NULL, NULL);
        PyDict_SetItemString(d, "Error", TripleDESCBCError);
}
}

