const sharp = require("sharp");
const fs = require("fs");
const path = require("path");
const QRCode = require("qrcode");
const { getCustomAvatar, getRandomAvatar } = require("./websocket_comfyUI");

// Function to get pillar template
function getPillarTemplate(pillar) {
  const scriptDir = __dirname;
  const templateBasePath = path.join(scriptDir, "Templates");
  const templatePath = path.join(templateBasePath, `${pillar}_TEMPLATE.png`);
  return templatePath;
}

// Function to create event pass
/**
 * Creates an event pass with the specified parameters.
 *
 * @param {string} pillar - Pillar Choice ("ASD", "CSD", "ESD", "EPD", "DAI", "SUTD" - SUTD is the generic one).
 * @param {string} chatID - To generate the QR Code.
 * @param {string} [name="Alex Tan"] - Name to be displayed on the event pass.
 * @param {boolean} [customAvatar=false] - Whether to use a custom avatar (only use customAvatar prior to Open House event).
 * @param {string} [avatarType="Male"] - Avatar type ("Male", "Female", other custom avatar choices - "Panda", "Fox", "Owl").
 * @param {string|null} [personalInterest=null] - Personal interest (only used if customAvatar is true).
 * @returns {Promise<string>} - The file path of the generated event pass.
 * @throws {Error} - Throws an error if there is an issue reading the template or avatar.
 */
async function createEventPass(
  pillar,
  chatID,
  name = "Alex Tan",
  customAvatar = false,
  avatarType = "Male",
  personalInterest = null
) {
  const templatePath = getPillarTemplate(pillar);
  let avatarName, tagline, avatarPath;
  if (customAvatar) {
    ({ avatarName, tagline, avatarPath } = await getCustomAvatar(
      avatarType,
      personalInterest
    ));
    console.log(avatarName, tagline, avatarPath);
  } else {
    ({ avatarName, tagline, avatarPath } = await getRandomAvatar(avatarType));
  }

  // Load the template and avatar
  let template, avatar;
  try {
    template = await sharp(templatePath).toBuffer();
  } catch (error) {
    console.error(`Error reading template: ${error.message}`);
    throw error;
  }
  try {
    avatar = await sharp(avatarPath).resize(420, 420).toBuffer();
  } catch (error) {
    console.error(`Error reading avatar: ${error.message}`);
    throw error;
  }

  // Create new pass
  const { width: passWidth, height: passHeight } = await sharp(
    template
  ).metadata();
  let eventPass = sharp({
    create: {
      width: passWidth,
      height: passHeight,
      channels: 4,
      background: { r: 255, g: 255, b: 255, alpha: 1 },
    },
  });

  // Composite template and avatar onto event pass
  const circleMask = Buffer.from(
    `<svg><circle cx="210" cy="210" r="210" /></svg>`
  );

  const circularAvatar = await sharp(avatar)
    .resize(420, 420)
    .composite([{ input: circleMask, blend: "dest-in" }])
    .png()
    .toBuffer();

  eventPass = eventPass.composite([
    { input: template, top: 0, left: 0 },
    { input: circularAvatar, top: 666, left: 330 },
  ]);

  // Add text elements
  const createTextImage = (
    text,
    fontFamily,
    fontSize,
    width,
    height,
    bold = true,
    italic = false
  ) => {
    const fontStyle = italic ? "italic" : "normal";
    const fontWeight = bold ? "bold" : "normal";
    const svgText = `
                <svg width="${width}" height="${height}">
                        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="${fontFamily}" font-size="${fontSize}" font-style="${fontStyle}" font-weight="${fontWeight}" fill="black">${text}</text>
                </svg>`;
    return Buffer.from(svgText);
  };

  // List of available sans-serif fonts
  const availableFonts = [
    "Arial",
    "Verdana",
    "Helvetica",
    "Tahoma",
    "Trebuchet MS",
    "Gill Sans",
    "Noto Sans",
    "Avantgarde",
    "Optima",
    "Arial Narrow",
  ];

  // Create text images
  const nameTextImage = createTextImage(
    name,
    availableFonts[3], // Replace with desired font from the list
    45,
    passWidth,
    75
  );
  const avatarNameTextImage = createTextImage(
    avatarName,
    availableFonts[3], // Replace with desired font from the list
    35,
    passWidth,
    60
  );
  const taglineTextImage = createTextImage(
    `"${tagline}"`,
    availableFonts[3], // Replace with desired font from the list
    30, // Smaller font size
    passWidth,
    60,
    (bold = false)
  );

  // Composite text images onto event pass
  eventPass = eventPass.composite([
    { input: template, top: 0, left: 0 },
    { input: circularAvatar, top: 666, left: 330 },
    { input: nameTextImage, top: 1145, left: 0 },
    { input: avatarNameTextImage, top: 1310, left: 0 },
    { input: taglineTextImage, top: 1380, left: 0 },
  ]);

  // Generate QR code
  const qrData = `SUTD_OH2025_${chatID}`;
  const qrImgBuffer = await QRCode.toBuffer(qrData, {
    width: 400,
    height: 400,
  });

  // Composite QR code onto event pass
  const qrX = (passWidth - 400) / 2;
  const qrY = 1517;
  eventPass = eventPass.composite([
    { input: template, top: 0, left: 0 },
    { input: circularAvatar, top: 666, left: 330 },
    { input: nameTextImage, top: 1145, left: 0 },
    { input: avatarNameTextImage, top: 1310, left: 0 },
    { input: taglineTextImage, top: 1380, left: 0 },
    { input: qrImgBuffer, top: qrY, left: qrX },
  ]);

  // Define output path
  const outputDir = path.join(__dirname, "FinalPass");
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
  }
  const outputPath = path.join(outputDir, `${chatID}_event_pass.png`);

  // Save event pass
  await eventPass.toFile(outputPath);
  //console.log(`Event pass saved to ${outputPath}`);

  return outputPath;
}

// Main function to run the script
(async () => {
  const pillar = "CSD"; // Replace with actual input
  const chatID = "1234"; // Replace with actual input
  const outputPath = await createEventPass(
    pillar,
    chatID,
    "Alex Tan",
    true,
    "Kangaroo",
    "computer scientist"
  );
  console.log(outputPath);
})();
