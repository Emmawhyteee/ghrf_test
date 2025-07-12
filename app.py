import sys
sys.dont_write_bytecode = True
from pkg import app

if __name__ == '__main__':
    port = 5000
    app.run(debug=True, port=port)

  