cunittest
===

In a project I've been working on, I recently found myself wanting to
run unittests concurrently. I did not, however, want mangled output to
the console. I also wanted the ability to pass in extra arguments to the
test cases that might be shared between threads (e.g. locks).

So, I hacked this together. It provides some Concurrent versions of the
built-in TestCase, TestSuite, and TextTestRunner objects. These weave
output together using cStringIO streams as buffers, and pass along extra
arguments to the run methods. 

The extra arguement passing is fragile, unfortunately, as the base
classes in unittest don't use *args and **kwargs in some of the run
methods.

Usage
===
See the example.py for usage. I've tried to ensure it's use and
interface matches the unittest library.

Copyright
===
Copyright (c) 2012 William J. Bowman wjb at williamjbowman dot com

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
