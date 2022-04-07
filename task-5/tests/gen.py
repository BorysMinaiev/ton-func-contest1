f = open("gen.fc", "w")

test_id = 52


def change_fun(who, now, expire, expect_action, exit_ok):
    global test_id

    public_key = "public_key1()" if who == 0 else "public_key2()"
    check_actions = "check_one_action(actions, {expire});".format(
        expire=expire) if expect_action else "check_no_actions(actions);"
    check_exit_code = "throw_if(100, exit_code != 0);" if exit_ok else "throw_if(100, exit_code == 0);"

    f.write("""
[int, tuple, cell, tuple, int] test_change_{test_id}_data() method_id({test_id}) {{
    return gen_test_now({public_key}, {expire}, {now}, {expire});
}}

_ test_change_{test_id}(int exit_code, cell data, tuple stack, cell actions, int gas) method_id({test_id_plus_1}) {{
    {check_exit_code}    
    {check_actions}
}}
    """.format(test_id=test_id, test_id_plus_1=test_id + 1, public_key=public_key, now=now, expire=expire,
               check_actions=check_actions, check_exit_code=check_exit_code))
    test_id = test_id + 2



import random

random.seed(787788)

now = 1000

values = {}

for _ in range(199):
    now += 3
    who = random.randint(0, 1)
    who_mask = 1 << who
    expire = random.randint(now, now + 60)

    exit_ok = True
    expect_action = False

    if expire in values:
        mask = values[expire]
        if (mask & who_mask) != 0:
            exit_ok = False
        else:
            nmask = mask | who_mask
            values[expire] = nmask
            if nmask == 3:
                expect_action = True
    else:
        cnt_already = 0
        for time in range(now, now + 61):
            if time in values:
                cnt_already += 1
        if cnt_already == 10:
            exit_ok = False
        else:
            values[expire] = who_mask

    change_fun(who, now, expire, expect_action, exit_ok)

f.close()
