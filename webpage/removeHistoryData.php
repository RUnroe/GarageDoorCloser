<?php

    $index = $_POST['index'];
    
    $dataObject = json_decode(file_get_contents("history.json"));
    if($index == "all"){
        while (count($dataObject->data) !=0){
            
        array_shift($dataObject->data);
        }
    }
    else{
        
        array_splice($dataObject->data,$index,1);
    }
    
    file_put_contents("history.json", json_encode($dataObject));
?>