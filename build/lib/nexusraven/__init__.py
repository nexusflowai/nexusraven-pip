from .client import Client

def create_client(api_key=None):
    return Client(api_key)


# Setting the Client class as a callable attribute of the module
__call__ = create_client

