# terminal 2
$ python -m lesson04.formatter
 * Running on http://127.0.0.1:8081/ (Press CTRL+C to quit)

# terminal 3
$ python -m lesson04.publisher
 * Running on http://127.0.0.1:8082/ (Press CTRL+C to quit)

 # Test
 curl 'http://localhost:8081/format?helloTo=Bryan'
 curl 'http://localhost:8082/publish?helloStr=hi%20there'

 # Completed test
 python -m lesson04.hello Bryan Bonjour