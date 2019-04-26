<?php 
    if($_SERVER["REQUEST_METHOD"]  == "GET") { 
        
        $doorState = $_REQUEST["state"];
        $timeout = $_REQUEST["timeout"];
        $setTimeHour = $_REQUEST["setTimeHour"];
        $setTimeMinute = $_REQUEST['setTimeMinute'];
        $currTimeHour = $_REQUEST['currTimeHour'];
        $currTimeMinute = $_REQUEST['currTimeMinute'];
        $myObject = json_decode(file_get_contents("data.json"));
        $myObject-> timeout = $timeout;
        $myObject-> setTimeHour = $setTimeHour;
        $myObject-> setTimeMinute = $setTimeMinute;
        
        
        date_default_timezone_set("America/Phoenix");
        $t=time();
        $date = date("m-d-y",$t);
        
        addUpdate($doorState, $currTimeHour, $currTimeMinute, $date);
        
        array_shift($myObject->stateArray);
        
        file_put_contents("data.json", json_encode($myObject));
        echo $date;
        
        
        if($myObject->stateArray[0]->doorState != $myObject->stateArray[1]->doorState){
            if($myObject->stateArray[0]->doorState > $myObject->stateArray[1]->doorState){
                //garage opened
                $stateChange = "Opened";
            }
            else{
                //garage closed
               $stateChange = "Closed";
            }
            $historyData = json_decode(file_get_contents("history.json"));
            
            $newHistoryData = new stdClass();
            $newHistoryData-> stateChange = $stateChange;
            $newHistoryData-> hour = $myObject->stateArray[1]->timeHour;
            $newHistoryData-> minute = $myObject->stateArray[1]->timeMinute;
            $newHistoryData-> Date = $myObject->stateArray[1]->day;
            array_push($historyData->data, $newHistoryData);
            file_put_contents("history.json", json_encode($historyData));
        }
    }
    
        
    function addUpdate($doorState, $currTimeHour, $currTimeMinute, $date){
        global $myObject;
        
        $obj = new stdClass();
        $obj-> doorState = $doorState;
        $obj-> timeHour = $currTimeHour;
        $obj-> timeMinute = $currTimeMinute;
        $obj-> day = $date;
        array_push($myObject->stateArray, $obj);
    }
    // use array_shift to get rid of the first element.
    // file put contents of data into history.json

//  https://programming2-rmunroe.c9users.io/garageDoor/dataInput.php?&state=1&timeout=20&setTimeHour=18&setTimeMinute=30&currTimeHour=16&currTimeMinute=12


?>

