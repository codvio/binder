# binder
Binds two incomming connection and provides message transfer between them.

Example command:

```
binder.py 1560 60000
```

The architecture may be like this for the above command:


```
                      B I N D E R
                     -------------
                     | INT |  E  |                 ------------
    -------> (60000) | SRV |  X  | (1560) <------- | DEVICE 1 |
                     |     |  T  |                 ------------
                     |-----|  E  |
                     | INT |  R  |                 ------------
    -------> (60001) | SRV |  N  | (1560) <------- | DEVICE 2 |
                     |     |  A  |                 ------------
                     |-----|  L  |
                     | INT |     |                 ------------
    -------> (60002) | SRV |  S  | (1560) <------- | DEVICE 3 |
                     |     |  E  |                 ------------
                     |-----|  R  |
                     | INT |  V  |                 ------------
    -------> (60003) | SRV |  E  | (1560) <------- | DEVICE 4 |
                     |     |  R  |                 ------------
                     -------------
```

**Binder** creates 1 external server that listens specific port for device connections. For every device connection it creates a new internal server starting with port 60000. After this. it transfers messages between matched internal and external connections.
