import { types as T, healthUtil } from "../deps.ts";

export const health: T.ExpectedExports.health = {
  "web-ui": healthUtil.checkWebUrl("http://invoicing-app.embassy:5005"),
  "dbgate": healthUtil.checkWebUrl("http://invoicing-app.embassy:3000")
};
