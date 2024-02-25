// 假设这是你的原始数组
const originalArray = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// 检查数组长度是否大于5
if (originalArray.length > 5) {
    // 提取第一个元素
    const firstElement = originalArray.slice(0, 1);
    // 提取最后四个元素
    const lastFourElements = originalArray.slice(-4);
    // 结合这两部分
    const newArray = firstElement.concat(lastFourElements);
    console.log(newArray); // 输出: [1, 7, 8, 9, 10]
} else {
    // 如果数组长度不超过5，直接使用原数组
    console.log(originalArray);
}
