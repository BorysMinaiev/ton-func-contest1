f = open("gen.fc", "w")

test_id = 22


def change_fun(use_prev_c4, key, valid_until, value):
    global test_id
    data = "get_prev_c4()" if use_prev_c4 else "begin_cell().end_cell()"

    f.write("""
[int, tuple, cell, tuple, int] test_change_{test_id}_data() method_id({test_id}) {{
    int function_selector = 0;

    slice message_body = begin_cell()
      .store_uint(1, 32) ;; add key
      .store_uint(12345, 64) ;; query id
      .store_uint({key}, 256) ;; key
      .store_uint({valid_until}, 64) ;; valid until
      .store_uint({value}, 128) ;; 128-bit value
      .end_cell().begin_parse();

    cell message = begin_cell()
            .store_uint(0x18, 6)
            .store_uint(0, 2) ;; should be contract address
            .store_grams(0)
            .store_uint(0, 1 + 4 + 4 + 64 + 32 + 1 + 1)
            .store_slice(message_body)
            .end_cell();

    ;; int balance, int msg_value, cell in_msg_full, slice in_msg_body
    tuple stack = unsafe_tuple([12345, 100, message, message_body]);

    cell data = {data};

    return [function_selector, stack, data, get_c7(), null()];
}}


_ test_change_{test_id}(int exit_code, cell data, tuple stack, cell actions, int gas) method_id({test_id_plus_1}) {{
    throw_if(100, exit_code != 0);
}}
    """.format(test_id=test_id, test_id_plus_1=test_id + 1, data=data, key=key, valid_until=valid_until, value=value))
    test_id = test_id + 2


def remove_old(now):
    global test_id

    f.write("""
[int, tuple, cell, tuple, int] test_remove_{test_id}_data() method_id({test_id}) {{
    int function_selector = 0;

    slice message_body = begin_cell()
      .store_uint(2, 32) ;; remove old
      .store_uint(12345, 64) ;; query id
      .end_cell().begin_parse();

    cell message = begin_cell()
            .store_uint(0x18, 6)
            .store_uint(0, 2) ;; should be contract address
            .store_grams(0)
            .store_uint(0, 1 + 4 + 4 + 64 + 32 + 1 + 1)
            .store_slice(message_body)
            .end_cell();

    ;; int balance, int msg_value, cell in_msg_full, slice in_msg_body
    tuple stack = unsafe_tuple([12345, 100, message, message_body]);

    cell data = get_prev_c4();

    return [function_selector, stack, data, get_c7_now({now}), null()];
}}


_ test_remove_{test_id}(int exit_code, cell data, tuple stack, cell actions, int gas) method_id({test_id_plus_1}) {{
    throw_if(100, exit_code != 0);
}}
    """.format(test_id=test_id, test_id_plus_1=test_id + 1, now=now))
    test_id = test_id + 2


def get_fun(key, expected_value, expected_valid_until):
    global test_id
    f.write("""
[int, tuple, cell, tuple, int] test_get_{test_id}_data() method_id({test_id}) {{
    int function_selector = 127977;

    tuple stack = unsafe_tuple([{key}]);
    cell data = begin_cell().end_cell();

    return [function_selector, stack, get_prev_c4(), get_c7(), null()];
}}


_ test_get_{test_id}(int exit_code, cell data, tuple stack, cell actions, int gas) method_id({test_id_plus_1}) {{
    throw_if(100, exit_code != 0);

    var valid_until = first(stack);
    throw_if(101, valid_until != {expected_valid_until});
    var value = second(stack);
    throw_if(102, value~load_uint(128) != {expected_value});
}}
""".format(test_id=test_id, test_id_plus_1=test_id + 1, key=key, expected_value=expected_value,
           expected_valid_until=expected_valid_until))
    test_id = test_id + 2


def get_fun_absent(key):
    global test_id
    f.write("""
[int, tuple, cell, tuple, int] test_get_{test_id}_data() method_id({test_id}) {{
    int function_selector = 127977;

    tuple stack = unsafe_tuple([{key}]);
    cell data = begin_cell().end_cell();

    return [function_selector, stack, get_prev_c4(), get_c7(), null()];
}}


_ test_get_{test_id}(int exit_code, cell data, tuple stack, cell actions, int gas) method_id({test_id_plus_1}) {{
    throw_if(100, exit_code == 0);
}}
""".format(test_id=test_id, test_id_plus_1=test_id + 1, key=key))
    test_id = test_id + 2

import random

change_fun(use_prev_c4=False, key=12345, valid_until=100, value=787788)
get_fun(key=12345, expected_value=787788, expected_valid_until=100)
get_fun_absent(key=12346)
remove_old(now=101)
get_fun_absent(key=12345)

now = 1000

values = {}

for _ in range(200):
    typ = random.randint(0, 10)
    if typ <= 4:
        key = random.randint(0, 10)
        value = random.randint(0, 10)
        valid_until = random.randint(now, now + 100)
        change_fun(use_prev_c4=True, key=key, value=value, valid_until=valid_until)
        values[key] = (value, valid_until)
    elif typ <= 9:
        key = random.randint(0, 10)
        if key in values:
            (expected_value, expected_value_until) = values[key]
            get_fun(key, expected_value=expected_value, expected_valid_until=expected_value_until)
        else:
            get_fun_absent(key)
    else:
        now = now + 50
        remove_old(now)
        to_remove = {}
        for key, vv in values.items():
            (value, valid_until) = vv
            if valid_until < now:
                to_remove[key] = True
        for key in to_remove.keys():
            del values[key]


f.close()
