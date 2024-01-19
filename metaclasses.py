import dis


class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        attrs = []

        for _, func in clsdict.items():
            try:
                instructions = dis.get_instructions(func)
            except TypeError:
                pass
            else:
                for i in instructions:
                    if i.opname == "LOAD_GLOBAL" and i.argval not in methods:
                        methods.append(i.argval)
                    elif i.opname == "LOAD_ATTR" and i.argval not in attrs:
                        attrs.append(i.argval)

        if "connect" in methods:
            raise TypeError("You can`t use method <connect> in ServerClass")

        if not ("SOCK_STREAM" in attrs and "AF_INET" in attrs):
            raise TypeError("Incorrect Socket")

        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []

        for _, func in clsdict.items():
            try:
                instructions = dis.get_instructions(func)
            except TypeError:
                pass
            else:
                for i in instructions:
                    if i.opname == "LOAD_GLOBAL" and i.argval not in methods:
                        methods.append(i.argval)

        for command in ("accept", "listen"):
            if command in methods:
                raise TypeError(f"You can`t use method {command} in ClientClass")

        if "get_message" in methods or "send_message" in methods:
            pass
        else:
            raise TypeError("Pass required methods <get_message> or <send_message>")

        super().__init__(clsname, bases, clsdict)
