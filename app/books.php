<?php
  $path = "books/"
  $books = json_encode(glob($path + "*.txt"));
  //header('Content-Type: application/json');
  //header('Content-Length: '.strlen($a));
  //header('Access-Control-Allow-Origin: *'); want to acces from crossdomain???
  echo $books;
?>
