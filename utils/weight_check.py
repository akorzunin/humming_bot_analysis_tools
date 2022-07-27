# %%
import  requests


# %%
def only(object,keys):
    obj = {}
    for path in keys:
        paths = path.split(".")
        rec=''
        origin = object
        target = obj
        for key in paths:
            rec += key
            if key in target:
                target = target[key]
                origin = origin[key]
                rec += '.'
                continue
            if key in origin:
                if rec == path:
                    target[key] = origin[key]
                else:
                    target[key] = {}
                target = target[key]
                origin = origin[key]
                rec += '.'
            else:
                target[key] = None
                break
    return obj

# %%
r = requests.get(
    url= 'https://api3.binance.com/api/v3/ping',
)

print(only(r.headers, ["x-mbx-used-weight","x-mbx-used-weight-1m"]))

