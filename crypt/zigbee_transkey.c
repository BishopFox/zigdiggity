/*
 * zigbee_transkey.c
 * 
 * 
 * original code from wireshark (packet-zbee-security.c)
 * originally adapted for SecBee (https://github.com/Cognosec/SecBee)
 * modified for use by ZigDiggity (https://github.com/bishopfox/zigdiggity)
 *
 * LICENSE INFORMATION: GNU General Public Lisence 2
 */
 
// Explaination of Python Build Values http://docs.python.org/c-api/arg.html#Py_BuildValue

#include <Python.h>
#include <stdio.h>
#include <gcrypt.h>

// We shouldn't do this, but we don't need the entire zigbee_crypt.c file if we embed the constant here.
#define ZBEE_SEC_CONST_BLOCKSIZE	16
#define ZBEE_SEC_CONST_KEYSIZE	16

/*FUNCTION:------------------------------------------------------
 *  NAME
 *      zbee_sec_hash
 *  DESCRIPTION
 *      ZigBee Cryptographic Hash Function, described in ZigBee
 *      specification sections B.1.3 and B.6.
 *
 *      This is a Matyas-Meyer-Oseas hash function using the AES-128
 *      cipher. We use the ECB mode of libgcrypt to get a raw block
 *      cipher.
 *
 *      Input may be any length, and the output must be exactly 1-block in length.
 *
 *      Implements the function:
 *          Hash(text) = Hash[t];
 *          Hash[0] = 0^(blocksize).
 *          Hash[i] = E(Hash[i-1], M[i]) XOR M[j];
 *          M[i] = i'th block of text, with some padding and flags concatenated.
 *  PARAMETERS
 *      char *    input       - Hash Input (any length).
 *      char      input_len   - Hash Input Length.
 *      char *    output      - Hash Output (exactly one block in length).
 *  RETURNS
 *      void
 *---------------------------------------------------------------
 */
static void zbee_sec_hash(char *input, int input_len, char *output)
{
    char              cipher_in[ZBEE_SEC_CONST_BLOCKSIZE];
    int               i, j;
    /* Cipher Instance. */
    gcry_cipher_hd_t    cipher_hd;
    
    /* Clear the first hash block (Hash0). */
    memset(output, 0, ZBEE_SEC_CONST_BLOCKSIZE);
    /* Create the cipher instance in ECB mode. */
    
    if (gcry_cipher_open(&cipher_hd, GCRY_CIPHER_AES128, GCRY_CIPHER_MODE_ECB, 0)) {
        return; 
    }
    //gcry_cipher_open(&cipher_hd, GCRY_CIPHER_AES128, GCRY_CIPHER_MODE_ECB, 0);
    /* Create the subsequent hash blocks using the formula: Hash[i] = E(Hash[i-1], M[i]) XOR M[i]
     *
     * because we can't garauntee that M will be exactly a multiple of the
     * block size, we will need to copy it into local buffers and pad it.
     *
     * Note that we check for the next cipher block at the end of the loop
     * rather than the start. This is so that if the input happens to end
     * on a block boundary, the next cipher block will be generated for the
     * start of the padding to be placed into.
     */
    i = 0;
    j = 0;
    while (i<input_len) {
        /* Copy data into the cipher input. */
        cipher_in[j++] = input[i++];
        /* Check if this cipher block is done. */
        if (j >= ZBEE_SEC_CONST_BLOCKSIZE) {
            /* We have reached the end of this block. Process it with the
             * cipher, note that the Key input to the cipher is actually
             * the previous hash block, which we are keeping in output.
             */
            (void)gcry_cipher_setkey(cipher_hd, output, ZBEE_SEC_CONST_BLOCKSIZE);
            (void)gcry_cipher_encrypt(cipher_hd, output, ZBEE_SEC_CONST_BLOCKSIZE, cipher_in, ZBEE_SEC_CONST_BLOCKSIZE);
            /* Now we have to XOR the input into the hash block. */
            for (j=0;j<ZBEE_SEC_CONST_BLOCKSIZE;j++) output[j] ^= cipher_in[j];
            /* Reset j to start again at the beginning at the next block. */
            j = 0;
        }
    } /* for */
    /* Need to append the bit '1', followed by '0' padding long enough to end
     * the hash input on a block boundary. However, because 'n' is 16, and 'l'
     * will be a multiple of 8, the padding will be >= 7-bits, and we can just
     * append the byte 0x80.
     */
    cipher_in[j++] = 0x80;
    /* Pad with '0' until the the current block is exactly 'n' bits from the
     * end.
     */
    while (j!=(ZBEE_SEC_CONST_BLOCKSIZE-2)) {
        if (j >= ZBEE_SEC_CONST_BLOCKSIZE) {
            /* We have reached the end of this block. Process it with the
             * cipher, note that the Key input to the cipher is actually
             * the previous hash block, which we are keeping in output.
             */
            (void)gcry_cipher_setkey(cipher_hd, output, ZBEE_SEC_CONST_BLOCKSIZE);
            (void)gcry_cipher_encrypt(cipher_hd, output, ZBEE_SEC_CONST_BLOCKSIZE, cipher_in, ZBEE_SEC_CONST_BLOCKSIZE);
            /* Now we have to XOR the input into the hash block. */
            for (j=0;j<ZBEE_SEC_CONST_BLOCKSIZE;j++) output[j] ^= cipher_in[j];
            /* Reset j to start again at the beginning at the next block. */
            j = 0;
        }
        /* Pad the input with 0. */
        cipher_in[j++] = 0x00;
    } /* while */
        /* Add the 'n'-bit representation of 'l' to the end of the block. */
    cipher_in[j++] = ((input_len * 8) >> 8) & 0xff;
    cipher_in[j] = ((input_len * 8) >> 0) & 0xff;
    /* Process the last cipher block. */
    (void)gcry_cipher_setkey(cipher_hd, output, ZBEE_SEC_CONST_BLOCKSIZE);
    (void)gcry_cipher_encrypt(cipher_hd, output, ZBEE_SEC_CONST_BLOCKSIZE, cipher_in, ZBEE_SEC_CONST_BLOCKSIZE);
    /* XOR the last input block back into the cipher output to get the hash. */
    for (j=0;j<ZBEE_SEC_CONST_BLOCKSIZE;j++) output[j] ^= cipher_in[j];
    /* Cleanup the cipher. */
    gcry_cipher_close(cipher_hd);
    /* Done */
} /* zbee_sec_hash */

/*FUNCTION:------------------------------------------------------
 *  NAME
 *      zbee_sec_key_hash
 *  DESCRIPTION
 *      ZigBee Keyed Hash Function. Described in ZigBee specification
 *      section B.1.4, and in FIPS Publication 198. Strictly speaking
 *      there is nothing about the Keyed Hash Function which restricts
 *      it to only a single byte input, but that's all ZigBee ever uses.
 *
 *      This function implements the hash function:
 *          Hash(Key, text) = H((Key XOR opad) || H((Key XOR ipad) || text));
 *          ipad = 0x36 repeated.
 *          opad = 0x5c repeated.
 *          H() = ZigBee Cryptographic Hash (B.1.3 and B.6).
 *
 *      The output of this function is an ep_alloced buffer containing
 *      the key-hashed output, and is garaunteed never to return NULL.
 *  PARAMETERS
 *      char  *key    - ZigBee Security Key (must be ZBEE_SEC_CONST_KEYSIZE) in length.
 *      char  input   - ZigBee CCM* Nonce (must be ZBEE_SEC_CONST_NONCE_LEN) in length.
 *      packet_info *pinfo  - pointer to packet information fields
 *  RETURNS
 *      char*
 *---------------------------------------------------------------
 */
static char *zbee_sec_key_hash(char *key, char input, char *hash_out)
{
    char              hash_in[2*ZBEE_SEC_CONST_BLOCKSIZE];
    int                 i;
    static const char ipad = 0x36;
    static const char opad = 0x5c;
    
    /* Copy the key into hash_in and XOR with opad to form: (Key XOR opad) */
    for (i=0; i<ZBEE_SEC_CONST_KEYSIZE; i++) hash_in[i] = key[i] ^ opad;
    /* Copy the Key into hash_out and XOR with ipad to form: (Key XOR ipad) */
    for (i=0; i<ZBEE_SEC_CONST_KEYSIZE; i++) hash_out[i] = key[i] ^ ipad;
    /* Append the input byte to form: (Key XOR ipad) || text. */
    hash_out[ZBEE_SEC_CONST_BLOCKSIZE] = input;
    /* Hash the contents of hash_out and append the contents to hash_in to
     * form: (Key XOR opad) || H((Key XOR ipad) || text).
     */
    zbee_sec_hash(hash_out, ZBEE_SEC_CONST_BLOCKSIZE+1, hash_in+ZBEE_SEC_CONST_BLOCKSIZE);
    /* Hash the contents of hash_in to get the final result. */
    zbee_sec_hash(hash_in, 2*ZBEE_SEC_CONST_BLOCKSIZE, hash_out);
    return hash_out;
} /* zbee_sec_key_hash */

static PyObject *zigbee_crypt_calc_transkey(PyObject *self, PyObject *args){
    char			*netKey;
    char				buffer[ZBEE_SEC_CONST_BLOCKSIZE+1];
    
    if (!PyArg_ParseTuple(args, "s", &netKey)) {
        PyErr_SetString(PyExc_ValueError, "incorrect key size (must be 16)");
        return NULL;
    }
    
    zbee_sec_key_hash(netKey, 0x00, buffer);
    
    return Py_BuildValue("s",buffer);

    //return buffer

};


static PyMethodDef zigbee_transkey_Methods[] = {
    { "calc_transkey", zigbee_crypt_calc_transkey, METH_VARARGS, "calc_transkey(networkkey) \n Calculates the Key used for Transport Key Encryption out of Network key"},
	{ NULL, NULL, 0, NULL },
};

PyMODINIT_FUNC initzigbee_transkey(void) {
	(void) Py_InitModule("zigbee_transkey", zigbee_transkey_Methods);
}

int main(int argc, char *argv[]) {
	Py_SetProgramName(argv[0]);
	Py_Initialize();
	initzigbee_transkey();
	return 0;
}
