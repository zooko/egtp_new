/*
 * Entropy gathering for Windows Machines.
 *
 * This should work on Win98 or later as well as machines with IE3 or greater.
 * For Win95 it will depend on your service pack. But you can alwasy download
 * the wincrypt module from MS. 
 *
 * artimage@ishiboo.com 2002
 *
 * Copyright (c) 2002 Artimage
 *
 * See end of file for License information.
 */

#include <Python.h>

#ifdef WIN32
#include <windows.h>     // for wincrypt.h
#include <wincrypt.h>

// Prototypes.
int entropy_get(unsigned char *data, const unsigned int amount); 
static PyObject *win_entropy_read(PyObject *self, PyObject *args);

static PyObject *
win_entropy_read(self, args)
     PyObject *self;    // This is a function not a method so this will always be NULL
     PyObject *args;
{
  int numBytes;         // How many bytes of entropy to get.
  PyObject * newstr;    // String of entropy we will return.

  unsigned char *data;  // Were we store entropy.

  // Get the args passed to this fcn.
  if (!PyArg_ParseTuple(args, "i", &numBytes)) {
    return NULL;
  }

  data = (unsigned char *) malloc(numBytes);
  
  entropy_get(data, numBytes); // Get the Entropy from the windows system.

  // BUGBUG does this actually make a string that is long enough? check num bytes returned.
  newstr = PyString_FromStringAndSize(data, numBytes); 
  if (newstr == NULL)
    return NULL; /* the Python/C API is that the function which returned NULL 
		    (PyString_FromStringAndSize) has already set the global PyErr 
		    value for us, so we just release any refcounts and return NULL. */
  
  free(data);

  return newstr;
}

int entropy_get(unsigned char *data, const unsigned int amount) {
  // This is voodoo magic I got from http://www.cs.berkeley.edu/~daw/rnd/cryptoapi-rand
  // It uses the MS Crytpo API to get us our entropy. It should work on  < Win98, WinNT, 
  // and any system that has IE3 or better. (So we are pretty well covered.)
  HCRYPTPROV hProvider = 0;
  CryptAcquireContext(&hProvider, 0, 0, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT);
  CryptGenRandom(hProvider, amount, data);

  return (0);
}

static PyMethodDef WinEntropyMethods[] = {
  {"read", win_entropy_read, METH_VARARGS, "Gather entropy from Windows OS."}, 
  {NULL, NULL, 0, NULL}
};

void
initwin_entropy(void)
{
  (void) Py_InitModule("win_entropy", WinEntropyMethods);
}


int main(int argc, char **argv)
{
  Py_SetProgramName(argv[0]);
  Py_Initialize();
  initwin_entropy();
  return 0;
}


#endif // WIN32

/*
 * License: 
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software to deal in this software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of this software, and to permit
 * persons to whom this software is furnished to do so, subject to the following
 * conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of this software.
 *
 * THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THIS SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THIS SOFTWARE.
 */
