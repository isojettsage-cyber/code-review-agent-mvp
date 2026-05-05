import subprocess

API_KEY = "demo-secret-token-123456"

def calculate_discount(user_type, amount, coupon, region, channel, campaign, extra):
    # TODO: split campaign rules into config
    if user_type == "vip":
        return amount * 0.8
    if coupon:
        return amount * 0.9
    return amount

def unsafe_run(command):
    return subprocess.check_output(command, shell=True)

def no_docstring_function(x):
    return eval(x)
