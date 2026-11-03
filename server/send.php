<?php
// Yorum isteme: WhatsApp + SMS'i InfiniReach üzerinden babanın 0505 hattından gönderir.
// Anahtarlar .htsecrets.php içinde (deploy sırasında GitHub secret'larından yazılır, repoda yok).
header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex, nofollow');
header('Cache-Control: no-store');

function out($code, $data) { http_response_code($code); echo json_encode($data, JSON_UNESCAPED_UNICODE); exit; }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(405, ['ok' => false, 'error' => 'POST gerekli']);

$S = @include __DIR__ . '/.htsecrets.php';
if (!is_array($S) || empty($S['key']) || empty($S['pin'])) out(500, ['ok' => false, 'error' => 'Sunucu ayarı eksik']);

$in = json_decode(file_get_contents('php://input'), true) ?: [];
$pin = (string)($_SERVER['HTTP_X_PIN'] ?? '');

$logFile = __DIR__ . '/.htlog.json';
$log = is_file($logFile) ? (json_decode(file_get_contents($logFile), true) ?: []) : [];
$now = time();
$phone = "";
$log['fails'] = array_values(array_filter($log['fails'] ?? [], function($t) use ($now, $phone) { return $t > $now - 3600; }));
if (count($log['fails']) >= 10) out(429, ['ok' => false, 'error' => 'Çok fazla hatalı PIN. 1 saat sonra deneyin.']);
if (!hash_equals((string)$S['pin'], $pin)) {
  $log['fails'][] = $now; file_put_contents($logFile, json_encode($log), LOCK_EX);
  out(401, ['ok' => false, 'error' => 'PIN hatalı']);
}
if (!empty($in['check'])) out(200, ['ok' => true]);

$phone = preg_replace('/\D/', '', (string)($in['phone'] ?? ''));
if (!preg_match('/^905\d{9}$/', $phone)) out(400, ['ok' => false, 'error' => 'Numara hatalı']);
$text = trim((string)($in['text'] ?? ''));
if ($text === '' || mb_strlen($text) > 1000 || strpos($text, $S['reviewUrl']) === false)
  out(400, ['ok' => false, 'error' => 'Mesaj geçersiz (yorum linki olmalı)']);

$log['sent'] = array_values(array_filter($log['sent'] ?? [], function($x) use ($now, $phone) { return $x['at'] > $now - 40 * 86400; }));
$today = count(array_filter($log['sent'], function($x) use ($now, $phone) { return $x['at'] > $now - 86400; }));
if ($today >= 15) out(429, ['ok' => false, 'error' => 'Günlük sınır (15 müşteri) doldu']);
$prev = array_values(array_filter($log['sent'], function($x) use ($now, $phone) { return $x['phone'] === $phone; }));
if ($prev && empty($in['force'])) out(409, ['ok' => false, 'dup' => true, 'at' => end($prev)['at'], 'error' => 'Bu numaraya daha önce gönderildi']);

function ir_send($S, $phone, $channel, $text) {
  $ch = curl_init('https://api.infinireach.io/api/v1/messages');
  curl_setopt_array($ch, [
    CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 20,
    CURLOPT_HTTPHEADER => ['Content-Type: application/json', 'X-API-Key: ' . $S['key']],
    CURLOPT_POSTFIELDS => json_encode(['to' => '+' . $phone, 'from' => $S['from'], 'channel' => $channel,
      'message' => $text, 'externalId' => $channel . '-' . $phone . '-' . date('Ymd')], JSON_UNESCAPED_UNICODE),
  ]);
  $body = curl_exec($ch); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
  $j = json_decode((string)$body, true);
  return ['ok' => $code >= 200 && $code < 300 && !empty($j['success']), 'code' => $code,
          'id' => $j['messageId'] ?? null, 'error' => $j['error'] ?? $j['message'] ?? null];
}

$res = [];
foreach ($S['channels'] as $c) $res[$c] = ir_send($S, $phone, $c, $text);
$any = array_filter($res, function($r) use ($now, $phone) { return $r['ok']; });
if ($any) { $log['sent'][] = ['phone' => $phone, 'at' => $now]; }
file_put_contents($logFile, json_encode($log), LOCK_EX);
out($any ? 200 : 502, ['ok' => (bool)$any, 'results' => $res]);
