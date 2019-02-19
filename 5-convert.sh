for i in `find locale -name symbols.po`; do
    msgfmt $i -o `echo $i|sed -e 's/\.po$/.mo/'`
done
