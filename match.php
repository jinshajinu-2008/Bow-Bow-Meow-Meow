<?php
include 'db.php';
header("Location: pet.php?id=" . $stmt->insert_id);
exit();

$id = $_GET['id'];

$currentPet = $conn->query("SELECT * FROM pets WHERE id = $id")->fetch_assoc();

$sql = "SELECT * FROM pets 
        WHERE id != ?
        AND breed = ?
        AND location = ?
        AND gender != ?
        AND ABS(age - ?) <= 2";

$stmt = $conn->prepare($sql);
$stmt->bind_param("isssi",
  $id,
  $currentPet['breed'],
  $currentPet['location'],
  $currentPet['gender'],
  $currentPet['age']
);

$stmt->execute();
$result = $stmt->get_result();
?>

<h2>Matches for <?php echo $currentPet['name']; ?></h2>

<?php
if ($result->num_rows == 0) {
    echo "<p>No matches found.</p>";
}

while ($row = $result->fetch_assoc()) {
    echo "<div style='border:1px solid #ccc;padding:15px;margin:10px;'>";
    echo "<h3>{$row['name']}</h3>";
    echo "<p>Breed: {$row['breed']}</p>";
    echo "<p>Age: {$row['age']}</p>";
    echo "<p>Color: {$row['color']}</p>";
    echo "<p>Location: {$row['location']}</p>";
    echo "</div>";
}
?>
