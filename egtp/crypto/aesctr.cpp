#include <iostream>             // for couts for debugging

#include "modes.h"
#include "aes.h"
#include "filters.h"

//extern "C"
//{
#include "Python.h"
//}

USING_NAMESPACE (CryptoPP)

PyObject *AESCTRError;

class MemoryException:public std::exception
{
public:
  explicit MemoryException ()
  {
  }
  virtual ~ MemoryException () throw ()
  {
  }
};

#define xdelete(p) delete (p); p = NULL
#define xdeletear(p) delete[] (p); p = NULL

typedef struct
{
  PyObject_HEAD;
  byte *key;
}
aesctr;

static PyObject *aesctr_new (aesctr * self, PyObject * args);

static void aesctr_delete (aesctr * self);

static PyObject *aesctr_encrypt (aesctr * self, PyObject * args);

static PyObject *aesctr_decrypt (aesctr * self, PyObject * args);

static PyObject *aesctr_getattr (aesctr * self, char *name);

statichere PyTypeObject aesctr_type = {
  PyObject_HEAD_INIT (&PyType_Type) 0,  /*ob_size */
  "AES-CTR",                    /*tp_name */
  sizeof (aesctr),              /*tp_size */
  0,                            /*tp_itemsize */
  /* methods */
  (destructor) aesctr_delete,   /*tp_dealloc */
  0,                            /*tp_print */
  (getattrfunc) aesctr_getattr, /*tp_getattr */
  0,                            /*tp_setattr */
  0,                            /*tp_compare */
  0,                            /*tp_repr */
  0,                            /*tp_as_number */
  0,                            /*tp_as_sequence */
  0,                            /*tp_as_mapping */
  0,                            /*tp_hash */
  0,                            /*tp_call */
  0,                            /*tp_str */
  0,                            /*tp_getattro */
  0,                            /*tp_setattro */
  0,                            /*tp_as_buffer */
  0,                            /*tp_xxx4 */
  0,                            /*tp_doc */
};

static PyMethodDef aesctr_methods[] = {
  {"encrypt", (PyCFunction) aesctr_encrypt, METH_VARARGS,
   "Returns an encrypted string.\n"
   "Accepts an initial counter string of length 16 and a plaintext string.\n"
   "Always returns a ciphertext of the exact same length as the plaintext."},
  {"decrypt", (PyCFunction) aesctr_decrypt, METH_VARARGS,
   "Returns a decrypted string.\n"
   "Accepts an initial counter string of length 16 and a ciphertext string.\n"
   "Always returns a plaintext of the exact same length as the ciphertext."},
  {NULL, NULL}                  /* sentinel */
};

static PyObject *
aesctr_getattr (aesctr * self, char *name)
{
  return Py_FindMethod (aesctr_methods, (PyObject *) self, name);
}

static void
aesctr_delete (aesctr * self)
{
  if (self != NULL)
    {
      xdeletear (self->key);
      PyMem_DEL (self);
    }
}

static PyObject *
aesctr_new (aesctr * self, PyObject * args)
{
  aesctr *newself = NULL;
  try
  {
    byte *key;
    int keylength;
    if (!PyArg_ParseTuple (args, "s#", &key, &keylength))
      {
        throw Exception (Exception::INVALID_ARGUMENT,
                         "wrong type of parameters passed in from Python");
      }
    if (keylength != 16)
      {
        throw Exception (Exception::INVALID_ARGUMENT,
                         "AES key length must be 16");
      }
    if (!(newself = PyObject_NEW (aesctr, &aesctr_type)))
      {
        throw MemoryException ();
      }
    byte *keycopy = new byte[16];
    memcpy (keycopy, key, 16);
    //              printf("in aesctr_new(); keycopy: %p, key: %p\n", keycopy, key);
    newself->key = keycopy;
    return (PyObject *) newself;
  }
  catch (CryptoPP::Exception & e)
  {
    aesctr_delete (newself);
    PyErr_SetString (AESCTRError, e.what ());
    return NULL;
  }
  catch (MemoryException & e)
  {
    aesctr_delete (newself);
    PyErr_SetString (PyExc_MemoryError,
                     "Can't allocate memory to do set up keys for en/decryption");
    return NULL;
  }
}

#define _MIN_UNSAFE(x, y) ((x)<(y)?(x):(y))
static PyObject *
aesctr_encrypt (aesctr * self, PyObject * args)
{
  //      std::cout << "hello enc 0" << std::endl; std::cout.flush();
  PyObject *result = NULL;
  byte *ciphertext = NULL;
  try
  {
    byte *initalcounter;
    unsigned int initalcounterlength;
    byte *text;
    unsigned int textlength;
    if (!PyArg_ParseTuple (args, "s#s#", &initalcounter, &initalcounterlength, &text, &textlength))
      {
        throw Exception (Exception::INVALID_ARGUMENT,
                         "wrong type of parameters passed in from Python");
      }
    if (initalcounterlength != 16)
      {
        throw Exception (Exception::INVALID_ARGUMENT, "initalcounter length must be 16");
      }
    //              std::cout << "hello enc 0.7" << std::endl; std::cout.flush();
    //              std::cout << "hello enc 0.7.1, self: " << self << std::endl; std::cout.flush();
    //              std::cout << "hello enc 0.7.2, self->key: ";
    //              std::cout << self->key;
    //              std::cout << std::endl;
    //              std::cout.flush();
    //      std::cout << "hello enc 0.7.3, iv: " << iv << std::endl; std::cout.flush();
    CTR_Mode < AES >::Encryption encryption (self->key, 16, initalcounter);
    //              std::cout << "hello enc 0.8" << std::endl; std::cout.flush();
    ciphertext = new byte[textlength];
    //              std::cout << "hello enc 0.9" << std::endl; std::cout.flush();
    if (ciphertext == NULL)
      {
        throw MemoryException ();
      }
    //              std::cout << "hello enc 1" << std::endl; std::cout.flush();
    StreamTransformationFilter encryptor (encryption,
                                          new ArraySink (ciphertext,
                                                         textlength));
    //              std::cout << "hello enc 2" << std::endl; std::cout.flush();
    encryptor.PutMessageEnd (text, textlength);
    //              std::cout << "hello enc 3" << std::endl; std::cout.flush();
    result = Py_BuildValue ("s#", ciphertext, textlength);
    //              std::cout << "hello enc 4" << std::endl; std::cout.flush();
    if (result == NULL)
      {
        throw MemoryException ();
      }
    //              std::cout << "hello enc 5" << std::endl; std::cout.flush();
    xdeletear (ciphertext);
    //              std::cout << "hello enc 6" << std::endl; std::cout.flush();
    return result;
  }
  catch (CryptoPP::Exception & e)
  {
    if (result != NULL)
      {
        PyMem_DEL (result);
      }
    xdeletear (ciphertext);
    PyErr_SetString (AESCTRError, e.what ());
    return NULL;
  }
  catch (MemoryException & e)
  {
    if (result != NULL)
      {
        PyMem_DEL (result);
      }
    xdeletear (ciphertext);
    PyErr_SetString (PyExc_MemoryError,
                     "Can't allocate memory to do encryption");
    return NULL;
  }
  //      std::cout << "goodbye enc" << std::endl; std::cout.flush();
}

static PyObject *
aesctr_decrypt (aesctr * self, PyObject * args)
{
  //      std::cout << "hello dec 0" << std::endl; std::cout.flush();
  PyObject *result = NULL;
  byte *plaintext = NULL;
  try
  {
    byte *initalcounter;
    unsigned int initalcounterlength;
    byte *text;
    unsigned int textlength;
    if (!PyArg_ParseTuple (args, "s#s#", &initalcounter, &initalcounterlength, &text, &textlength))
      {
        throw Exception (Exception::INVALID_ARGUMENT,
                         "wrong type of parameters passed in from Python");
      }
    if (initalcounterlength != 16)
      {
        throw Exception (Exception::INVALID_ARGUMENT, "initalcounter length must be 16");
      }
    CTR_Mode < AES >::Decryption decryption (self->key, 16, initalcounter);
    plaintext = new byte[textlength];
    if (plaintext == NULL)
      {
        throw MemoryException ();
      }
    StreamTransformationFilter decryptor (decryption,
                                          new ArraySink (plaintext,
                                                         textlength));
    decryptor.PutMessageEnd (text, textlength);
    result = Py_BuildValue ("s#", plaintext, textlength);
    if (result == NULL)
      {
        throw MemoryException ();
      }
    xdeletear (plaintext);
    return result;
  }
  catch (CryptoPP::Exception & e)
  {
    if (result != NULL)
      {
        PyMem_DEL (result);
      }
    xdeletear (plaintext);
    PyErr_SetString (AESCTRError, e.what ());
    return NULL;
  }
  catch (MemoryException & e)
  {
    if (result != NULL)
      {
        PyMem_DEL (result);
      }
    xdeletear (plaintext);
    PyErr_SetString (PyExc_MemoryError,
                     "Can't allocate memory to do decryption");
    return NULL;
  }
}

PyMethodDef aesctr_functions[] = {
  {"new", (PyCFunction) aesctr_new, METH_VARARGS,
   "Constructs a new aesctr.\n" "Accepts a key of length 16."}
  ,
  {NULL, NULL}                  /* Sentinel */
};

char *aesctr_doc =
  "Does 3DES encryption and decyption in CBC mode with ciphertext stealing.\n"
  "Always uses a key of length 16 and initialization vectors of length 8.\n"
  "\n"
  "Class methods are - \n"
  "new(key) - constructor\n"
  "\n"
  "Instance methods are - \n"
  "encrypt(initalcounter, plaintext) - encrypt a string\n"
  "decrypt(initalcounter, ciphertext) - decrypt a string";

/* Initialize this module. */

extern "C"
{
  DL_EXPORT (void) initaesctr ()
  {
    PyObject *m, *d;
      m = Py_InitModule3 ("aesctr", aesctr_functions, aesctr_doc);
      d = PyModule_GetDict (m);
      AESCTRError = PyErr_NewException ("aesctr.Error", NULL, NULL);
      PyDict_SetItemString (d, "Error", AESCTRError);
  }
}
