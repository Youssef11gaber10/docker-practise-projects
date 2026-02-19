import { readFile } from "fs";
readFile("./src/app.ts", (err, data) => {
  if (err) { throw err; }
  // tslint:disable-next-line:no-console
  console.log(data.toString());
});
