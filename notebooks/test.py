import pyotp
import base64
import binascii


def generate_totp(secret_key):
    totp = pyotp.TOTP(secret_key)
    otp = totp.now()
    return otp


def validate_totp(secret_key, user_input):
    totp = pyotp.TOTP(secret_key)

    return totp.verify(user_input)


def is_base32(s):
    try:
        base64.b32decode(s, casefold=True)
        return True
    except binascii.Error:
        return False


if __name__ == '__main__':
    secret_key = pyotp.random_base32()

    if is_base32(secret_key):
        print("Секретный ключ корректен.")
    else:
        print("Секретный ключ некорректен.")

    print(f"Секретный ключ (храните в безопасности): {secret_key}")

    generated_otp = generate_totp(secret_key)
    print(f"Сгенерированный одноразовый пароль: {generated_otp}")


    user_input = input("Введите одноразовый пароль: ")
    if validate_totp(secret_key, user_input):
        print("Пароль верен. Доступ разрешен.")
    else:
        print("Пароль неверен. Доступ запрещен.")


