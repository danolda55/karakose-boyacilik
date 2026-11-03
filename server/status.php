<?php
// Gönderilen mesajların durumunu (sent/delivered/failed) sorar.
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
$S = @include __DIR__ . '/.htsecrets.php';
if (!is_array($S) || !hash_equals((string)$S['pin'], (string)($_SERVER['HTTP_X_PIN'] ?? ''))) { http_response_code(401); echo '{"ok":false}'; exit; }
$id = preg_replace('/[^a-zA-Z0-9]/', '', (string)($_GET['id'] ?? ''));
if ($id === '') { http_response_code(400); echo '{"ok":false}'; exit; }
$ch = curl_init('https://api.infinireach.io/api/v1/messages/' . $id);
curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15, CURLOPT_HTTPHEADER => ['X-API-Key: ' . $S['key']]]);
$b = curl_exec($ch); curl_close($ch);
$j = json_decode((string)$b, true);
echo json_encode(['ok' => true, 'status' => $j['message']['status'] ?? null], JSON_UNESCAPED_UNICODE);
