def is_msg_stat(s):
    return s.content_type == 'text' and len(s.text) <= 2 and s.text.isdigit() \
           and not (len(s.text) == 2 and s.text[0] == '0')
