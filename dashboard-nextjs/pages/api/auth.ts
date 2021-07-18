// Next.js API route support: https://nextjs.org/docs/api-routes/introduction

import axios, { AxiosError } from "axios";
import { NextApiRequest, NextApiResponse } from "next";

export default function (req: NextApiRequest, res: NextApiResponse) {
  const url = req.body.url;
  const loginURL = process.env.API_BASE_URL + url;
  console.log("base", loginURL);

  axios.post(loginURL).then(
    (data) => {
      res.status(200).json(data.data);
    },
    (err: AxiosError) => {
      res.status(503).json(err.message);
    }
  );
}
