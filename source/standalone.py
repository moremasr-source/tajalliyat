"""Wrap dist/index.html (authored for the Claude artifact host, which adds the <head> skeleton)
into a complete standalone page for GitHub Pages."""
import sys, pathlib
src = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
head = '''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
'''
pathlib.Path(sys.argv[2]).write_text(head + src + '\n</html>\n', encoding='utf-8')
