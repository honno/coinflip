# Recorded with the doitlive recorder
#doitlive shell: /bin/bash
#doitlive prompt: default

```ipython
from coinflip.randtests import monobits
result = monobits([0, 1, 0, 0, 1])
print(result)
result2 = monobits(["bob", "alice", "bob", "bob", "alice"])
print(result2)
result3 = monobits(["bob", "alice", "matthew"])
from coinflip.randtests import discrete_fourier_transform
result4 = discrete_fourier_transform([0, 1, 0, 0, 1])
print(result4)
from coinflip.randtests import binary_matrix_rank
result5 = binary_matrix_rank([0, 1, 0, 0, 1])
print(result5)
result6 = binary_matrix_rank([0, 1, 0])
```

firefox https://coinflip.readthedocs.io/


