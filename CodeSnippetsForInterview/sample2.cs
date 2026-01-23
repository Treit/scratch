if (!string.IsNullOrEmpty(context.Data))
{
    var list = context.Data.Split(";").ToList();
    if (list.Count > 0)
    {
        foreach (var item in list)
        {
            var itemInfo = item.Split(":").ToList();
            if (itemInfo.Count == 2 && itemInfo[0] == Constants.Label)
            {
                Req.Add(Constants.Label, itemInfo[1]);
            }
        }
    }
}

