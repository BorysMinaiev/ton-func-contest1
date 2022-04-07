
import ed25519

PRIVATE = bytes.fromhex(
    '35a18e5c796bfa7c22b9dbd4cb57ce990da253ea6d40c7c4ef00040685c5eeb2' +
    'd9ac7c0682a097dbe84a53df6a72a11135be337b71445a056406a37cc024cd0a')
PUBLIC = bytes.fromhex('d9ac7c0682a097dbe84a53df6a72a11135be337b71445a056406a37cc024cd0a')

signing_key = ed25519.SigningKey(PRIVATE)

print(hex(801854338641936177776183129953942598386721085129997706921155269871225682425))

sign = signing_key.sign(bytes.fromhex('01c5d55e72ce510c51b7ca648c0b75566d12744c5e7253af2aa4c45b67be39f9'), encoding='hex')

print(sign[0:64])
print(sign[64:])