const cells = document.querySelectorAll('.cell');
cells.forEach(cell => cell.addEventListener('click', handleCellClick));

function handleCellClick() {
    const row = this.dataset.row;
    const col = this.dataset.col;
    document.querySelector('#row').value = row;
    document.querySelector('#col').value = col;
    document.querySelector('#form').submit();
}