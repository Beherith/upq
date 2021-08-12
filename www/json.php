<?php
require("config.php");
require("include/drupal_dummy.inc");
require("include/search.inc");

function json_search($req){
	$res=search($req);
	for($i=0; $i<count($res); $i++){
		if(array_key_exists('torrent', $res[$i])){
			$res[$i]['torrent']=base64_encode($res[$i]['torrent']);
		}
	}
	return $res;
}

function main($argv){
	$req=array(
		"springname"=>"%",
		"torrent"=>"true"
	);
	$res=json_search($req);
	echo json_encode($res);
}

function JsonResult($request)
{
	return json_encode(json_search($request));
}

if (array_key_exists('argv', $_SERVER))
	main($_SERVER['argv']);
else
	if ($_SERVER['REQUEST_METHOD']=="GET"){
		header('Access-Control-Allow-Origin: *');
		$cb = $_REQUEST['callback'];
		if (isset($cb) && !empty($cb)) {
			header('Content-Type: application/javascript;charset=utf-8');
			$cb = preg_replace('/[^a-zA-Z0-9]/', '', $cb); // strip anything except a-Z0-9
			echo ($cb .'(' . JsonResult($_REQUEST) . ');');
		} else {
			header('Content-Type: application/json;charset=utf-8');
			$cb = preg_replace('/[^a-zA-Z0-9]/', '', $cb); // strip anything except a-Z0-9
			echo JsonResult($_REQUEST);
		}
	} else {
		echo file_get_contents("readme.html");
		return;
	}

