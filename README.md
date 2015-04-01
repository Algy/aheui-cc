# AheuiCC
What is AheuiCC
--
AheuiCC(아희씨씨)는 아희 코드를 실행가능한 파일로 변환시키는 컴파일러입니다. 

Usage
--
```
python ahcc.py [-o executable] filename
```

Performance
--
C로짠 구현체(https://github.com/aheui/caheui.git) 보다 x95배 빠릅니다!
```
$ time ./aheui .snippets/logo/logo.aheui > logo.png 
23.38s user 0.08s system 99% cpu 23.611 total
```
```
$ aheuicc|master⚡ ⇒ python ahcc.py -o logo_program snippets/logo/logo.aheui  
$ time ./logo_program > logo.png
0.23s user 0.01s system 94% cpu 0.249 total
```

Disclamer
--
소스 워킹 트리에 포함된 어셈블러는 알파희(https://github.com/aheui/rpaheui) 의 것을 사용하였습니다.
