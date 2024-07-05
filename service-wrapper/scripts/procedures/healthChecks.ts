import { types as T, healthUtil } from "../deps.ts";

export const health: T.ExpectedExports.health = {
  async "web-ui"(effects, duration) {
    try {
      return await healthUtil.checkWebUrl("http://invoicing.embassy:5005")(effects, duration);
    } catch (error) {
      return healthUtil.catchError(effects)(error);
    }
  },
};
